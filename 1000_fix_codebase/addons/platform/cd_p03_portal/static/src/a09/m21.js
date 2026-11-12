/** @odoo-module **/
/* A09 · People & Workforce — M21 Core HR & Lifecycle (full build; the meta
 * stub it replaces showed one screen and wrong KPIs).
 * Registry-faithful: 4 groups / 12 screens / 5 reports / 4 forms / freg 70. */

export const MODULE = {
  area: 'A09', code: 'M21', en: 'Core HR & Lifecycle', title: 'M21 · Core HR & Lifecycle',
  bn: 'মানবসম্পদ ও জীবনচক্র', icon: '👥',
  desc: 'Employee directory and record, org chart and positions, hire and onboarding, transfer and promotion, exit and settlement, movement history, appointment letters, service books, dependants and nominees, and ESS/MSS self-service.',
  kpis: [
    { l: 'Headcount', m: 'headcount' },
    { l: 'Attrition YTD', m: 'attrition_ytd', suffix: '%' },
    { l: 'Technicians', m: 'technicians' },
    { l: 'Open Positions', m: 'open_positions' },
    { l: 'Probation Ending (30d)', m: 'probation_ending_30d' },
    { l: 'Service Books', m: 'service_books_complete' }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M21-leave-type', en: "Leave Type", bn: "ছুটির ধরন", t: 'g' }
    ]},
    { en: 'Employee Master', screens: [
      { id: 'M21-directory', en: 'Directory', bn: 'কর্মী তালিকা', t: 'g' },
      { id: 'M21-employee', en: 'Employee Record', bn: 'কর্মী নথি', t: 'f' },
      { id: 'M21-orgchart', en: 'Org Chart', bn: 'সংগঠন চার্ট', t: 'r' },
      { id: 'M21-positions', en: 'Positions & Jobs', bn: 'পদ', t: 'g' },
      { id: 'M21-education', en: 'Academic Qualifications', bn: 'শিক্ষাগত যোগ্যতা', t: 'g' },
      { id: 'M21-experience', en: 'Work Experience', bn: 'কর্মঅভিজ্ঞতা', t: 'g' }
    ]},
    { en: 'Lifecycle', screens: [
      { id: 'M21-hire', en: 'Hire / Onboard', bn: 'নিয়োগ', t: 'g' },
      { id: 'M21-transfer', en: 'Transfer / Promote', bn: 'স্থানান্তর ও পদোন্নতি', t: 'g' },
      { id: 'M21-exit', en: 'Exit & Settlement', bn: 'প্রস্থান', t: 'g' },
      { id: 'M21-master-change', en: 'Master Changes', bn: 'তথ্য পরিবর্তন', t: 'g' },
      { id: 'M21-disciplinary', en: 'Disciplinary', bn: 'শৃঙ্খলা', t: 'g' },
      { id: 'M21-abandonment', en: 'Absence Without Leave (s.27(3A))', bn: 'বিনা ছুটিতে অনুপস্থিতি', t: 'g' },
      { id: 'M21-movement', en: 'Movement History', bn: 'চলাচলের ইতিহাস', t: 'r' }
    ]},
    { en: 'Documents', screens: [
      { id: 'M21-appointment', en: 'Appointment Letters', bn: 'নিয়োগপত্র', t: 'g' },
      { id: 'M21-servicebook', en: 'Service Books', bn: 'সার্ভিস বুক', t: 'g' },
      { id: 'M21-nominees', en: 'Dependants & Nominees', bn: 'মনোনীত ব্যক্তি', t: 'g' }
    ]},
    { en: 'Self-Service', screens: [
      { id: 'M21-ess', en: 'ESS / MSS', bn: 'স্ব-সেবা', t: 'r' }
    ]},
    /* A09 round 2: the identity read log (HR Manager) and the read-only
     * clean-up findings the business decides from. */
    { en: 'Governance', screens: [
      { id: 'M21-rpt-identity-log', en: 'Identity Read Log', bn: 'পরিচয় তথ্য পাঠের লগ', t: 'r' },
      { id: 'M21-rpt-cleanup', en: 'Data Clean-up Findings', bn: 'তথ্য পরিচ্ছন্নতা', t: 'r' }
    ]}
  ],
  reports: ['Headcount & Movement', 'Attrition Analysis', 'Probation Conversion', 'Establishment Register', 'Org Distribution', 'Form 6(a) Register', 'Identity Read Log', 'Data Clean-up Findings'],
  forms: ['Employee', 'Transfer', 'Promotion', 'Exit Clearance'],
  cross: ['M02 Dispatch', 'M56 Payroll', 'M55 Attendance', 'M57 Incentives'],
  freg: { src: 70, sub: [
    ['1', 'Employee Master', 12, { model: 'hr.employee', cols: ['name', 'employee_code', 'position_id', 'operating_unit_id', 'employment_type'], screens: ['M21-directory', 'M21-employee', 'M21-education', 'M21-experience'], reports: ['Identity Read Log', 'Data Clean-up Findings'], forms: ['Employee'] }],
    ['2', 'Employment Contracts', 7, { model: 'fix.employment.contract', cols: ['employee_id', 'contract_type', 'joining_date', 'probation_end', 'state'], screens: ['M21-hire'], reports: ['Probation Conversion'], forms: [] }],
    ['3', 'Org Structure', 9, { model: 'fix.org.position', cols: ['name', 'parent_id', 'grade', 'operating_unit_id'], screens: ['M21-positions', 'M21-orgchart'], reports: ['Org Distribution', 'Establishment Register'], forms: [] }],
    ['4', 'Lifecycle Events', 12, { model: 'fix.hr.transfer', cols: ['name', 'employee_id', 'movement_type', 'effective_date', 'state'], screens: ['M21-transfer', 'M21-movement'], reports: ['Headcount & Movement'], forms: ['Transfer', 'Promotion'] }],
    ['5', 'Statutory Documents', 7, { model: 'fix.hr.document', cols: ['name', 'employee_id', 'doc_type', 'issued_on', 'verified'], screens: ['M21-appointment', 'M21-servicebook'], reports: ['Form 6(a) Register'], forms: [] }],
    ['6', 'Dependants & Nominees', 5, { model: 'fix.hr.dependant', cols: ['employee_id', 'name', 'relation', 'is_nominee', 'nominee_pct'], screens: ['M21-nominees'], reports: [], forms: [] }],
    ['7', 'ESS / MSS', 9, { model: 'hr.employee', cols: ['name', 'employee_code', 'employment_type', 'joining_date', 'confirmation_date'], screens: ['M21-ess'], reports: ['Probation Conversion'], forms: [], create: false }],
    ['8', 'Exit Process', 9, { model: 'fix.hr.exit', cols: ['name', 'employee_id', 'exit_type', 'last_working_day', 'state'], screens: ['M21-exit'], reports: ['Attrition Analysis'], forms: ['Exit Clearance'] }]
  ] }
};

export const SCREENS = {
  'M21-directory': { kind: 'model_list', model: 'hr.employee',
    cols: ['name', 'employee_code', 'position_id', 'operating_unit_id', 'job_title', 'work_email', 'active'],
    /* A09 P0-b: Form 6(a) is a report pack (M21-rpt-form6a): the action
     * returned a list the endpoint dropped. Leaver and KPI-090 confirmation
     * are on screen (HR / HR manager only, server-checked). */
    actions: [
      { m: 'action_generate_form6_appointment', l: 'Generate Form 6 Appointment' },
      { m: 'action_generate_form7_service_book', l: 'Generate Form 7 Service Book' },
      { m: 'action_generate_id_card', l: 'Issue ID Card' },
      { m: 'action_record_psr_submission', l: 'Record PSR Submission' },
      { m: 'action_verify_psr', l: 'Verify PSR (second person)' },
      { m: 'action_mark_psr_exempt', l: 'Mark PSR Exempt' },
      { m: 'action_mark_left', l: 'Record Leaver' },
      { m: 'action_confirm_keycloak_deprovisioned', l: 'Confirm Keycloak Deprovisioned' }
    ] },
  'M21-orgchart': { kind: 'table_report', module: 'M21', report: 'org_distribution', title: 'Org Distribution', period: true },
  'M21-positions': { kind: 'model_list', model: 'fix.org.position',
    cols: ['name', 'parent_id', 'grade', 'headcount', 'filled_count', 'vacant_count', 'operating_unit_id', 'company_id'] },
  'M21-hire': { kind: 'model_list', model: 'fix.employment.contract', stateField: 'state',
    cols: ['employee_id', 'contract_type', 'joining_date', 'probation_end', 'date_end', 'basic_monthly', 'legal_signoff_state', 'approval_state', 'state'],
    /* The legal sign-off is decided in Legal Counsel's approval inbox (M63);
     * a contract ends through its exit, never by a Terminate button. */
    actions: [
      { m: 'action_request_legal_signoff', l: 'Request Legal Signoff', states: ['draft'] },
      { m: 'action_recall_approval', l: 'Recall Signoff Request', states: ['draft'] },
      { m: 'action_activate', l: 'Activate', states: ['draft'] },
      { m: 'action_new_version', l: 'New Version', states: ['active'] },
      { m: 'action_confirm_probation', l: 'Confirm Probation', states: ['active'] },
      { m: 'action_extend_probation', l: 'Extend Probation (skilled)', states: ['active'] },
      { m: 'action_generate_contract_document', l: 'Generate Contract Document' }
    ] },
  'M21-transfer': { kind: 'model_list', model: 'fix.hr.transfer', stateField: 'state',
    cols: ['name', 'employee_id', 'movement_type', 'effective_date', 'from_position_id', 'to_position_id', 'state'],
    /* Each step is its owner's (line manager, destination manager,
     * evaluator, HR, Finance); the executive decision is routed (M63). */
    actions: [
      { m: 'action_recommend', l: 'Recommend', states: ['draft'] },
      { m: 'action_concur', l: 'Concur', states: ['recommended'] },
      { m: 'action_tech_eval', l: 'Technical Evaluation', states: ['recommended', 'concurred'] },
      { m: 'action_hr_audit', l: 'HR Audit', states: ['concurred', 'tech_evaluated'] },
      { m: 'action_finance_approve', l: 'Finance Clearance', states: ['hr_audited'] },
      { m: 'action_request_approval', l: 'Request Executive Approval', states: ['hr_audited', 'finance_approved'] },
      { m: 'action_recall_approval', l: 'Recall Approval Request', states: ['hr_audited', 'finance_approved'] },
      { m: 'action_tick_open_jobs', l: 'Open Jobs Audited', states: ['approved'] },
      { m: 'action_tick_toolkit', l: 'Tool Kit Returned', states: ['approved'] },
      { m: 'action_tick_spare_parts', l: 'Spare Parts Reconciled', states: ['approved'] },
      { m: 'action_tick_storekeeper', l: 'Storekeeper Cleared', states: ['approved'] },
      { m: 'action_tick_imprest', l: 'Imprest Settled', states: ['approved'] },
      { m: 'action_clear_handover', l: 'Clear Handover', states: ['approved'] },
      { m: 'action_apply', l: 'Apply Movement', states: ['handover_cleared'] },
      { m: 'action_reset_draft', l: 'Reset to Draft' },
      { m: 'action_cancel', l: 'Cancel' }
    ] },
  'M21-exit': { kind: 'model_list', model: 'fix.hr.exit', stateField: 'state',
    cols: ['name', 'employee_id', 'exit_type', 'last_working_day', 'clearance_it', 'clearance_finance', 'clearance_hr', 'clearance_assets', 'settlement_amount', 'settlement_due_date', 'approval_state', 'state'],
    /* Each clearance tick has one owner (IT, Finance, HR, Assets). The
     * settlement figure is payroll's (I1) and Finance approves it from the
     * approval inbox; there is no Settle button. */
    actions: [
      { m: 'action_confirm_notice', l: 'Confirm Exit & Notice', states: ['draft'] },
      { m: 'action_clear_it', l: 'IT Clearance', states: ['notice'] },
      { m: 'action_clear_finance', l: 'Finance Clearance', states: ['notice'] },
      { m: 'action_clear_hr', l: 'HR Clearance', states: ['notice'] },
      { m: 'action_clear_assets', l: 'Assets Clearance', states: ['notice'] },
      { m: 'action_clear', l: 'Complete Clearance', states: ['notice'] },
      { m: 'action_compute_settlement', l: 'Compute Settlement (Payroll)', states: ['cleared'] },
      { m: 'action_request_approval', l: 'Route Settlement to Finance', states: ['cleared'] },
      { m: 'action_recall_approval', l: 'Recall Settlement Request', states: ['cleared'] },
      { m: 'action_create_settlement_payment', l: 'Create Settlement Payment (Payroll)', states: ['settled'] },
      { m: 'action_issue_service_certificate', l: 'Issue Service Certificate (s.31)', states: ['cleared', 'settled'] },
      { m: 'action_cancel', l: 'Cancel', states: ['draft', 'notice'] }
    ] },
  /* BLA s.27(3A): HR serves the notice; the cron opens the self-defence
   * window and routes the deemed resignation to the executive's inbox. */
  'M21-abandonment': { kind: 'model_list', model: 'fix.hr.abandonment', stateField: 'state',
    cols: ['name', 'employee_id', 'absence_start_date', 'absent_days', 'notice_date', 'reply_due', 'hearing_due', 'approval_state', 'exit_id', 'state'],
    actions: [
      { m: 'action_issue_notice', l: 'Serve s.27(3A) Notice', states: ['draft'] },
      { m: 'action_record_explanation', l: 'Record Explanation / Rejoined', states: ['noticed', 'hearing', 'decision'] },
      { m: 'action_request_approval', l: 'Request Decision', states: ['hearing'] },
      { m: 'action_recall_approval', l: 'Recall Decision Request', states: ['decision'] },
      { m: 'action_cancel', l: 'Cancel', states: ['draft', 'noticed', 'hearing', 'decision'] }
    ] },
  'M21-movement': { kind: 'table_report', module: 'M21', report: 'headcount_movement', title: 'Movement History', period: true },
  'M21-appointment': { kind: 'model_list', model: 'fix.hr.document',
    cols: ['name', 'employee_id', 'doc_type', 'reference', 'issued_on', 'generated', 'verified', 'acknowledged'],
    actions: [
      { m: 'action_verify', l: 'Verify (second person)' },
      { m: 'action_unverify', l: 'Withdraw Verification' },
      { m: 'action_acknowledge', l: 'Acknowledge (the employee)' }
    ] },
  'M21-servicebook': { kind: 'model_list', model: 'fix.hr.document',
    cols: ['name', 'employee_id', 'reference', 'issued_on', 'verified', 'acknowledged', 'notes'],
    actions: [
      { m: 'action_verify', l: 'Verify (second person)' },
      { m: 'action_acknowledge', l: 'Acknowledge (the employee)' }
    ] },
  'M21-nominees': { kind: 'model_list', model: 'fix.hr.dependant',
    cols: ['employee_id', 'name', 'relation', 'date_of_birth', 'is_nominee', 'nominee_pct'] },
  'M21-ess': { kind: 'table_report', module: 'M21', report: 'probation_conversion', title: 'ESS / MSS — Probation Conversions Due', period: true },

  /* Report chips -> their own computed pack */
  'M21-rpt-headcount': { kind: 'table_report', module: 'M21', report: 'headcount_movement', title: 'Headcount & Movement', period: true },
  'M21-rpt-attrition': { kind: 'table_report', module: 'M21', report: 'attrition_analysis', title: 'Attrition Analysis', period: true },
  'M21-rpt-probation': { kind: 'table_report', module: 'M21', report: 'probation_conversion', title: 'Probation Conversion', period: true },
  'M21-rpt-establishment': { kind: 'table_report', module: 'M21', report: 'establishment_register', title: 'Establishment Register', period: true },
  'M21-rpt-form6a': { kind: 'table_report', module: 'M21', report: 'form6a_register', title: 'Form 6(a) Worker Register (BLR r.20)', period: false },
  'M21-rpt-identity-log': { kind: 'table_report', module: 'M21', report: 'identity_access_log', title: 'Identity Read Log (BRU-HCM-07, HR Manager)', period: true },
  'M21-rpt-cleanup': { kind: 'table_report', module: 'M21', report: 'data_cleanup', title: 'Data Clean-up Findings (read-only)', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M21-employee': {
    kind: 'model_form',
    model: 'hr.employee',
    title: 'Employee Record',
    back: 'M21-directory',
    tabs: [
      { id: 'identity', label: 'Identity & Bio', bn: 'ব্যক্তিগত ও পরিচয়', icon: '👤', badge: '12' },
      { id: 'statutory', label: 'Statutory & Tax', bn: 'সংবিধিবদ্ধ ও কর', icon: '⚖️', badge: '14' },
      { id: 'organization', label: 'Organization & Role', bn: 'প্রতিষ্ঠান ও পদায়ন', icon: '🏢', badge: '12' },
      { id: 'academic', label: 'Academic & Education', bn: 'শিক্ষাগত যোগ্যতা', icon: '🎓', badge: '11' },
      { id: 'career', label: 'Career & Experience', bn: 'কর্মজীবন ও অভিজ্ঞতা', icon: '💼', badge: '11' },
      { id: 'technical', label: 'Skills & Certifications', bn: 'কারিগরি দক্ষতা ও সনদ', icon: '🔧', badge: '10' },
      { id: 'compensation', label: 'Compensation & Banking', bn: 'বেতন ও ব্যাংকিং', icon: '💵', badge: '12' },
      { id: 'health', label: 'Health, HSE & Fitness', bn: 'স্বাস্থ্য ও ফিটনেস', icon: '🩺', badge: '8' },
      { id: 'emergency', label: 'Emergency & Nominees', bn: 'জরুরি ও নমিনী', icon: '🆘', badge: '12' },
      { id: 'vault', label: 'Document Vault', bn: 'নথিপত্র ভল্ট', icon: '📁', badge: '8' }
    ],
    sections: [
      // ================= TAB 1: IDENTITY & BIO =================
      {
        tab: 'identity',
        title: 'Official Corporate Identity',
        note: 'Corporate master identification, biometric credentials, and system login endpoints.',
        fields: [
          { name: 'image_1920', label: 'Employee Photo', type: 'image' },
          { name: 'name', required: true, label: 'Employee Legal Name (English)' },
          { name: 'name_bn', label: 'Full Legal Name (Bengali Script)' },
          { name: 'employee_code', label: 'Employee Code' },
          { name: 'biometric_id', label: 'Biometric Attendance Device PIN' },
          { name: 'work_email', label: 'Corporate Work Email' },
          { name: 'mobile_phone', label: 'Work Mobile / Fleet SIM' }
        ]
      },
      {
        tab: 'identity',
        title: 'Personal Legal Identity & Demographics',
        note: 'Statutory demographic identity required under Bangladesh Labour Act 2006 Form 7 Service Book.',
        fields: [
          { name: 'father_name', label: "Father's Name" },
          { name: 'mother_name', label: "Mother's Name" },
          { name: 'birthday', label: 'Date of Birth' },
          { name: 'sex', label: 'Gender' },
          { name: 'marital', label: 'Marital Status' }
        ]
      },
      {
        tab: 'identity',
        title: 'Social, Cultural & Physical Demographics',
        note: 'Physical safety metrics, identification mark, and religion for statutory festival bonuses.',
        fields: [
          { name: 'blood_group', label: 'Blood Group' },
          { name: 'religion', label: 'Religion (Festival Bonus Category)' },
          { name: 'identification_mark', label: 'Physical Identification Mark' }
        ]
      },
      {
        tab: 'identity',
        title: 'Present & Permanent Residential Address',
        note: 'Current operational residence versus ancestral permanent domicile required under BLA Rule 23.',
        fields: [
          { name: 'private_street', label: 'Present Street / Holding / Apt' },
          { name: 'private_city', label: 'Present Thana / Upazila' },
          { name: 'private_district', label: 'Present District' },
          { name: 'permanent_address', label: 'Permanent Address (Village/Road/Post)' },
          { name: 'permanent_district', label: 'Permanent District' },
          { name: 'permanent_division', label: 'Permanent Division' }
        ]
      },

      // ================= TAB 2: STATUTORY & TAX =================
      {
        tab: 'statutory',
        title: 'National Identity & Civil Registrations',
        note: 'Civil registrations, National ID verification, Form 7 Service Book (15-day update clock under BLR rr.19-21), and international passport.',
        fields: [
          { name: 'nid_number', label: 'National ID (10-digit Smart / 17-digit NID)' },
          { name: 'birth_reg_number', label: 'Birth Registration Number (17-digit BRIS)' },
          { name: 'service_book_number', label: 'Form 7 Service Book Register No' },
          { name: 'form7_last_event_date', label: 'Form 7 Last Change Event Date' },
          { name: 'form7_endorsed_on', label: 'Form 7 Last Endorsed Date', readonly: true },
          { name: 'form7_update_due_date', label: 'Form 7 15-Day Update Due Date', readonly: true },
          { name: 'form7_update_overdue', label: 'Form 7 Update Overdue', readonly: true },
          { name: 'passport_number', label: 'International Passport Number' }
        ]
      },
      {
        tab: 'statutory',
        title: 'NBR Direct Taxation (Income Tax Act 2023)',
        note: 'Mandatory compliance with ITA 2023 Sections 261 & 264 Proof of Submission of Return (PSR).',
        fields: [
          { name: 'tin_number', label: '12-Digit e-TIN Number (NBR)' },
          { name: 'tax_zone', label: 'NBR Tax Zone' },
          { name: 'tax_circle', label: 'NBR Tax Circle' },
          { name: 'psr_ack_number', label: 'Return Ack No (PSR / Form 23)' },
          { name: 'psr_status', label: 'PSR Compliance Status (ITA s.264)', readonly: true },
          { name: 'psr_tax_year', label: 'PSR Assessment Year' },
          { name: 'psr_verified_on', label: 'PSR Verification Date', readonly: true },
          { name: 'psr_qr_payload', label: 'PSR Verification QR / URL' },
          { name: 'taxpayer_category', label: 'Taxpayer Slab Category' },
          { name: 'minimum_tax_location', label: 'Minimum Tax Liability Area' },
          { name: 'has_disabled_child', label: 'Parent of Disabled Child (BDT 50,000 Relief)' }
        ]
      },
      {
        tab: 'statutory',
        title: 'Field Mobility & Driving Credentials',
        note: 'BRTA driving license credentials governing motorcycle/van field technician dispatch.',
        fields: [
          { name: 'driving_license_no', label: 'BRTA Driving License Number' },
          { name: 'driving_license_type', label: 'License Vehicle Class' },
          { name: 'driving_license_exp', label: 'License Expiration Date' }
        ]
      },
      {
        tab: 'statutory',
        title: 'Background Verification & Integrity',
        note: 'Police clearance certificate and verification record for high-trust customer premises dispatch.',
        fields: [
          { name: 'police_clearance_ref', label: 'Police Clearance Certificate Ref (PCC)' }
        ]
      },

      // ================= TAB 3: ORGANIZATION & ROLE =================
      {
        tab: 'organization',
        title: 'Corporate Structure & Operating Unit',
        note: 'Placement within the corporate hierarchy, tenant operating unit, and physical workplace.',
        fields: [
          { name: 'company_id', label: 'Company Entity' },
          { name: 'operating_unit_id', label: 'Branch / Operating Unit Hub' },
          { name: 'department_id', label: 'Corporate Department' },
          { name: 'work_location_type', label: 'Workplace Category (Workshop/Field/Office)' }
        ]
      },
      {
        tab: 'organization',
        title: 'Designation, Position & Classification',
        note: 'Job band, establishment position, reporting manager, and BLA worker classification.',
        fields: [
          { name: 'job_title', label: 'Designation / Job Title' },
          { name: 'job_band', label: 'Corporate Grade / Band (Band 1 - Band 8)' },
          { name: 'position_id', label: 'Establishment Position' },
          { name: 'parent_id', label: 'Reporting Manager' },
          { name: 'employment_type', label: 'BLA Worker Classification' }
        ]
      },
      {
        tab: 'organization',
        title: 'Lifecycle Dates & Probation Tracking',
        note: 'Statutory continuous service milestones and probation duration capped under Labour Rules r.25.',
        fields: [
          { name: 'joining_date', label: 'Date of Joining' },
          { name: 'probation_months', label: 'Probation Duration (Cap 6 Months)' },
          { name: 'confirmation_date', label: 'Permanent Confirmation Date' }
        ]
      },
      {
        tab: 'organization',
        title: 'System Permissions & Security Identity',
        note: 'Keycloak Identity Provider UUID and automated deprovisioning status (KPI-090).',
        fields: [
          { name: 'keycloak_id', label: 'Keycloak IdP UUID' },
          { name: 'keycloak_deprovision_status', label: 'IdP Deprovision Status (KPI-090)', readonly: true }
        ]
      },

      // ================= TAB 4: ACADEMIC & EDUCATION =================
      {
        tab: 'academic',
        title: 'Primary Educational Qualification',
        note: 'Highest academic credential, board/university accreditation, and degree title.',
        fields: [
          { name: 'degree_level', label: 'Highest Education Level' },
          { name: 'degree_title', label: 'Degree / Diploma Title' },
          { name: 'major_group', label: 'Field of Study / Major' },
          { name: 'board_university', label: 'Education Board / University' },
          { name: 'institute_name', label: 'School / College / Institute' }
        ]
      },
      {
        tab: 'academic',
        title: 'Academic Performance & Audit Verification',
        note: 'Passing year, certified grading score, and physical/online board verification audit.',
        fields: [
          { name: 'passing_year', label: 'Passing Year' },
          { name: 'result_type', label: 'Grading System' },
          { name: 'gpa_score', label: 'Secured GPA / Score' },
          { name: 'roll_number', label: 'Academic Roll Number' },
          { name: 'registration_no', label: 'Board Registration Number' },
          { name: 'academic_verified', label: 'Verification Audit Status', readonly: true }
        ]
      },

      // ================= TAB 5: CAREER & EXPERIENCE =================
      {
        tab: 'career',
        title: 'Prior Employment Track',
        note: 'Previous employer organization, industry sector, and job designation held.',
        fields: [
          { name: 'prev_company_name', label: 'Previous Employer Name' },
          { name: 'prev_industry_type', label: 'Previous Industry Sector' },
          { name: 'prev_designation', label: 'Previous Position Held' },
          { name: 'prev_start_date', label: 'Start Date' },
          { name: 'prev_end_date', label: 'End Date' },
          { name: 'prev_experience_years', label: 'Total Prior Experience (Years)' }
        ]
      },
      {
        tab: 'career',
        title: 'Separation & Reference Check Signoff',
        note: 'Last drawn compensation, separation rationale, and documented HR reference verification.',
        fields: [
          { name: 'prev_last_salary', label: 'Last Drawn Gross Salary (BDT)' },
          { name: 'prev_reason_leaving', label: 'Separation Reason' },
          { name: 'prev_supervisor_name', label: 'Previous Supervisor Name' },
          { name: 'prev_supervisor_phone', label: 'Supervisor Contact Mobile' },
          { name: 'prev_reference_status', label: 'Reference Check Signoff', readonly: true }
        ]
      },

      // ================= TAB 6: SKILLS & CERTIFICATIONS =================
      {
        tab: 'technical',
        title: 'Technical Repair Capability Classification',
        note: 'Component-level repair hierarchy (L1–L4) gating automated work order dispatch.',
        fields: [
          { name: 'repair_tier', label: 'Technical Repair Capability Tier (L1-L4)' },
          { name: 'device_competencies', label: 'Supported Device Specializations' },
          { name: 'esd_certified', label: 'ESD Safe Handling Protocol Certified' },
          { name: 'bga_rework_capable', label: 'BGA Rework Station Authorized Operator' }
        ]
      },
      {
        tab: 'technical',
        title: 'OEM Brand Accreditations & Badges',
        note: 'Authorized OEM manufacturer certifications required for brand warranty claims.',
        fields: [
          { name: 'oem_brand_certs', label: 'OEM Brand Accreditations (Apple/Samsung/HP/Daikin)' },
          { name: 'certification_no', label: 'Primary Technical Certificate No' },
          { name: 'cert_issue_date', label: 'Certificate Issue Date' },
          { name: 'cert_expiry_date', label: 'Certificate Expiration Date' }
        ]
      },
      {
        tab: 'technical',
        title: 'Tool Kit Custody & Quality Undertakings',
        note: 'Precision calibration custody and anti-extraction confidentiality compliance.',
        fields: [
          { name: 'toolkit_custody_ref', label: 'Assigned Tool Kit Barcode Ref' },
          { name: 'customer_nda_signed', label: 'Customer Data Confidentiality Undertaking (NDA)', readonly: true }
        ]
      },

      // ================= TAB 7: COMPENSATION & BANKING =================
      {
        tab: 'compensation',
        title: 'Monthly Compensation Structure (BDT)',
        note: 'Comprehensive salary package breakdown under corporate pay scale.',
        fields: [
          { name: 'wage', label: 'Monthly Gross Salary (BDT)' },
          { name: 'basic_wage', label: 'Monthly Basic Wage (BDT)' },
          { name: 'house_rent', label: 'House Rent Allowance (BDT)' },
          { name: 'medical_allowance', label: 'Medical Allowance (BDT)' },
          { name: 'conveyance_allowance', label: 'Conveyance Allowance (BDT)' },
          { name: 'technical_allowance', label: 'Technical Skill / OEM Allowance (BDT)' }
        ]
      },
      {
        tab: 'compensation',
        title: 'Statutory Scheme Eligibility',
        note: 'Overtime entitlement at double rate (BLA s.108) and Provident Fund membership.',
        fields: [
          { name: 'overtime_eligible', label: 'Overtime Eligible (BLA s.108 Double Rate)' },
          { name: 'pf_member', label: 'Recognized Provident Fund (RPF) Member' }
        ]
      },
      {
        tab: 'compensation',
        title: 'Scheduled Bank Account (BEFTN / NPSB)',
        note: 'Scheduled commercial bank account and 9-digit BEFTN routing number for salary transfers.',
        fields: [
          { name: 'bank_name', label: 'Scheduled Bank Name' },
          { name: 'bank_branch_name', label: 'Branch Name' },
          { name: 'routing_number', label: '9-Digit BEFTN Routing Code' },
          { name: 'bank_account_number', label: 'Bank Account Number' }
        ]
      },
      {
        tab: 'compensation',
        title: 'Mobile Financial Services (MFS Wallets)',
        note: 'Personal mobile financial wallet for technician daily travel allowance and field expenses.',
        fields: [
          { name: 'mfs_provider', label: 'MFS Provider (bKash / Nagad / Rocket / Upay)' },
          { name: 'mfs_account_number', label: 'MFS Account Number (01XXXXXXXXX)' }
        ]
      },

      // ================= TAB 8: HEALTH, HSE & FITNESS =================
      {
        tab: 'health',
        title: 'Physical Metrics & Baseline Vitals',
        note: 'Pre-employment medical clearance and color vision test for soldering/resistor coding.',
        fields: [
          { name: 'color_blindness', label: 'Color Vision Test Status (Ishihara Test)' },
          { name: 'medical_fitness', label: 'Medical Fitness Verdict' },
          { name: 'work_restrictions', label: 'Physical Work Restrictions' }
        ]
      },
      {
        tab: 'health',
        title: 'Occupational Vaccinations & Insurance',
        note: 'Mandatory occupational immunizations and corporate group insurance policy coverage.',
        fields: [
          { name: 'tetanus_vaccine_date', label: 'Tetanus Toxoid (TT) Vaccination Date' },
          { name: 'tetanus_expiry_date', label: 'Tetanus Booster Expiration Date' },
          { name: 'chemical_allergies', label: 'Chemical / Solvent Allergies' },
          { name: 'insurance_policy_no', label: 'Corporate Group Insurance Policy No' }
        ]
      },

      // ================= TAB 9: EMERGENCY & NOMINEES =================
      {
        tab: 'emergency',
        title: 'Primary Emergency Next-of-Kin Contact',
        note: 'Statutory primary emergency contact person for workplace accidents under BLA 2006.',
        fields: [
          { name: 'emergency_contact', required: true, label: 'Primary Emergency Contact Person' },
          { name: 'emergency_contact_relation', label: 'Relationship' },
          { name: 'emergency_phone', required: true, label: 'Primary Emergency Phone' },
          { name: 'emergency_phone_alt', label: 'Alternative Emergency Phone' },
          { name: 'emergency_contact_address', label: 'Emergency Contact Full Address' }
        ]
      },
      {
        tab: 'emergency',
        title: 'Secondary Emergency Contact',
        note: 'Backup contact endpoint in event primary next-of-kin is unreachable.',
        fields: [
          { name: 'emergency_contact_sec', label: 'Secondary Emergency Contact Person' },
          { name: 'emergency_relation_sec', label: 'Relationship' },
          { name: 'emergency_phone_sec', label: 'Secondary Emergency Phone' }
        ]
      },
      {
        tab: 'emergency',
        title: 'Family Particulars & Dependants',
        note: 'Spouse and children particulars recorded for group medical coverage.',
        fields: [
          { name: 'spouse_name', label: 'Spouse Legal Name' },
          { name: 'children', label: 'Number of Dependent Children' }
        ]
      },
      {
        tab: 'emergency',
        title: 'Statutory Nominee Designation (BLA s. 19 & 131)',
        note: 'Designated statutory nominee entitled to terminal death/retirement benefits (must sum to 100%).',
        fields: [
          { name: 'nominee_name', label: 'Primary Statutory Nominee Legal Name' },
          { name: 'nominee_relation', label: 'Nominee Relationship' },
          { name: 'nominee_nid', label: 'Nominee NID / Birth Certificate No' },
          { name: 'nominee_pct', label: 'Entitlement Share % (BLA s.19)' },
          { name: 'guardian_name', label: 'Legal Guardian Name (if Nominee is Minor)' }
        ]
      },

      // ================= TAB 10: DOCUMENT VAULT =================
      {
        tab: 'vault',
        title: 'Statutory Identity & Tax Document Scans',
        note: 'Upload scanned copies of government identification and tax registration certificates.',
        fields: [
          { name: 'doc_nid_file', label: 'National ID Smart Card (Scanned File)', type: 'file' },
          { name: 'doc_nid_verified', label: 'National ID Smart Card Verified', readonly: true },
          { name: 'doc_tin_file', label: '12-digit e-TIN Certificate (Scanned File)', type: 'file' },
          { name: 'doc_tin_verified', label: '12-digit e-TIN Certificate Verified', readonly: true },
          { name: 'doc_psr_file', label: 'Tax Return Submission Ack (PSR Scan)', type: 'file' },
          { name: 'doc_psr_verified', label: 'Tax Return Submission Ack (PSR) Verified', readonly: true }
        ]
      },
      {
        tab: 'vault',
        title: 'Employment Contracts & Statutory Registers',
        note: 'Signed appointment letter, Form 7 service book register, and employee confidentiality agreements.',
        fields: [
          { name: 'doc_appointment_file', label: 'Signed Appointment Letter (Scanned File)', type: 'file' },
          { name: 'doc_appointment_signed', label: 'Signed Appointment Letter on File', readonly: true },
          { name: 'doc_service_book_file', label: 'Form 7 Service Book Pages (Scanned File)', type: 'file' },
          { name: 'doc_service_book_scanned', label: 'Form 7 Service Book Pages Scanned', readonly: true },
          { name: 'doc_nda_file', label: 'Signed NDA & Code of Conduct (Scanned File)', type: 'file' },
          { name: 'doc_nda_signed', label: 'Signed NDA & Code of Conduct on File', readonly: true }
        ]
      },
      {
        tab: 'vault',
        title: 'Health, Safety & Background Clearance Scans',
        note: 'Medical fitness certifications and police clearance certificates.',
        fields: [
          { name: 'doc_medical_file', label: 'Medical Fitness Certificate (Scanned File)', type: 'file' },
          { name: 'doc_medical_fit_certified', label: 'Medical Fitness Certificate Signed', readonly: true },
          { name: 'doc_police_pcc_file', label: 'Police Clearance Certificate (PCC Scan)', type: 'file' },
          { name: 'doc_police_pcc_cleared', label: 'Police Clearance Certificate (PCC) Cleared', readonly: true }
        ]
      },
      {
        tab: 'vault',
        title: 'Academic Credentials & Nominee Records',
        note: 'Scanned highest educational/vocational certificates and statutory nominee documents.',
        fields: [
          { name: 'doc_academic_file', label: 'Highest Academic / Trade Certificate (Scanned File)', type: 'file' },
          { name: 'doc_nominee_nid_file', label: 'Statutory Nominee NID & Photo (Scanned File)', type: 'file' }
        ]
      }
    ]
  },
  'M21-form-contract': {
    kind: 'model_form',
    model: 'fix.employment.contract',
    title: 'Hire / Employment Contract',
    back: 'M21-hire',
    status: { field: 'state', labels: {
      draft: 'Draft', active: 'Active', expired: 'Expired', terminated: 'Terminated',
      superseded: 'Superseded' } },
    tabs: [
      { id: 'terms', label: 'Employment Terms', bn: 'নিয়োগের শর্তাবলী', icon: '📄', badge: '5' },
      { id: 'compensation', label: 'Remuneration & Hours', bn: 'বেতন ও কর্মঘণ্টা', icon: '⏱️', badge: '4' },
      { id: 'signoff', label: 'Governance & Legal', bn: 'আইনি অনুমোদন', icon: '✍️', badge: '4' }
    ],
    sections: [
      {
        tab: 'terms',
        title: 'Appointment Terms & Contract Profile',
        note: 'Labour Rules 2015 Form 6 appointment structure. Probation capped at 6 months under Rule 25.',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'contract_type', required: true, label: 'Contract Type' },
          { name: 'joining_date', required: true, label: 'Joining Date' },
          { name: 'probation_class', label: 'Probation Class (BLA s.4(8): 6 / 3 / 3+3 months)' },
          { name: 'probation_end', label: 'Probation End Date' },
          { name: 'date_end', label: 'Contract End Date (fixed term)' },
          { name: 'effective_date', label: 'Version Terms Effective From' },
          { name: 'operating_unit_id', label: 'Branch / Operating Unit' },
          { name: 'probation_decision', label: 'Probation Decision', readonly: true },
          { name: 'previous_contract_id', label: 'Previous Version', readonly: true }
        ]
      },
      {
        tab: 'compensation',
        title: 'Remuneration & Statutory Working Hours',
        note: 'Basic monthly salary, contract allowances (House Rent, Medical, Conveyance, Technical), and s. 102 statutory ceiling of 48 hours/week.',
        fields: [
          { name: 'basic_monthly', required: true, label: 'Basic Monthly Salary (BDT)' },
          { name: 'house_rent', label: 'House Rent Allowance (BDT)' },
          { name: 'medical_allowance', label: 'Medical Allowance (BDT)' },
          { name: 'conveyance_allowance', label: 'Conveyance Allowance (BDT)' },
          { name: 'technical_allowance', label: 'Technical Skill Allowance (BDT)' },
          { name: 'other_allowance', label: 'Other Monthly Allowance (BDT)' },
          { name: 'weekly_hours', required: true, label: 'Weekly Hours (Max 48 s.102)' },
          { name: 'currency_id', label: 'Currency' },
          { name: 'state', required: true, label: 'Contract State', readonly: true }
        ]
      },
      {
        tab: 'signoff',
        title: 'M24 Governance & Legal Counsel Signoff',
        note: 'Statutory density score (+52% Category H) and legal signoff control before activation.',
        fields: [
          { name: 'template_id', label: 'M24 Form 6 Contract Template' },
          { name: 'statutory_density_score', label: 'Statutory Density Score (%)' },
          { name: 'legal_signoff_state', label: 'Legal Counsel Signoff State', readonly: true },
          { name: 'signed_by_legal_counsel', label: 'Approved Legal Counsel', readonly: true },
          { name: 'legal_signoff_on', label: 'Signed Off On', readonly: true },
          { name: 'approval_state', label: 'Routed Approval (M63)', readonly: true }
        ]
      }
    ]
  },

  'M21-form-transfer': {
    kind: 'model_form',
    model: 'fix.hr.transfer',
    title: 'Transfer / Promotion Dossier',
    back: 'M21-transfer',
    status: {
      field: 'state',
      labels: {
        draft: 'Draft Requisition',
        recommended: 'Recommended',
        concurred: 'Destination Concurred',
        tech_evaluated: 'Tech Evaluated',
        hr_audited: 'HR Audited',
        finance_approved: 'Finance Cleared',
        approved: 'Executive Approved',
        handover_cleared: 'Handover Cleared',
        applied: 'Applied to Master',
        cancelled: 'Cancelled',
        rejected: 'Rejected'
      }
    },
    tabs: [
      { id: 'movement', label: 'Movement Scope', bn: 'স্থানান্তর পরিধি', icon: '📋', badge: '11' },
      { id: 'organization', label: 'Position & Org Realignment', bn: 'পদ ও সাংগঠনিক বিন্যাস', icon: '🏢', badge: '10' },
      { id: 'compensation', label: 'Compensation & Payroll', bn: 'বেতন ও ভাতা', icon: '💰', badge: '10' },
      { id: 'technical', label: 'Technical Tier & OEM Badges', bn: 'কারিগরি স্তর ও ওইএম ব্যাজ', icon: '🔬', badge: '10' },
      { id: 'handover', label: 'Handover & Custody Clearance', bn: 'হস্তান্তর ও জিম্মা ছাড়পত্র', icon: '🔧', badge: '12' },
      { id: 'logistics', label: 'Relocation & Transit Leave', bn: 'স্থানান্তর ভাতা ও ট্রানজিট ছুটি', icon: '🚚', badge: '9' },
      { id: 'approval', label: 'Authorization & Digital Signoff', bn: 'অনুমোদন ও ডিজিটাল স্বাক্ষর', icon: '✍️', badge: '6 Gates' },
      { id: 'vault', label: 'Document Vault & Physical Scans', bn: 'নথিপত্র ভল্ট ও স্ক্যান', icon: '📁', badge: '7 Scans' }
    ],
    sections: [
      // ================= TAB 1: MOVEMENT SCOPE =================
      {
        tab: 'movement',
        title: 'Movement Requisition & Scope',
        note: 'Movement category, employee selection, effective timeline, and operational justification.',
        fields: [
          { name: 'name', label: 'Movement Reference', readonly: true },
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'movement_type', required: true, label: 'Movement Type' },
          { name: 'movement_category', required: true, label: 'Movement Category' },
          { name: 'movement_nature', required: true, label: 'Movement Nature' },
          { name: 'deputation_months', label: 'Deputation Duration (Months)' },
          { name: 'initiator_user_id', label: 'Requisition Initiated By', readonly: true },
          { name: 'requisition_date', label: 'Requisition Date' },
          { name: 'release_date', label: 'Proposed Release Date' },
          { name: 'effective_date', required: true, label: 'Effective / Joining Date' },
          { name: 'reason', label: 'Operational Justification' },
          { name: 'state', required: true, label: 'Workflow State', readonly: true }
        ]
      },

      // ================= TAB 2: ORG REALIGNMENT =================
      {
        tab: 'organization',
        title: 'Branch & Department Realignment',
        note: 'Source and destination branch hubs and functional departments.',
        fields: [
          { name: 'from_operating_unit_id', label: 'Current Branch' },
          { name: 'to_operating_unit_id', required: true, label: 'Destination Branch' },
          { name: 'from_department_id', label: 'Current Department' },
          { name: 'to_department_id', label: 'Destination Department' }
        ]
      },
      {
        tab: 'organization',
        title: 'Position, Grade & Reporting Hierarchy',
        note: 'Establishment position slot, corporate grade band, and direct reporting manager.',
        fields: [
          { name: 'from_position_id', label: 'Current Position' },
          { name: 'to_position_id', required: true, label: 'Destination Position' },
          { name: 'from_job_title', label: 'Current Job Title' },
          { name: 'to_job_title', label: 'Destination Job Title' },
          { name: 'from_grade_band', label: 'Current Corporate Grade' },
          { name: 'to_grade_band', label: 'Destination Corporate Grade' },
          { name: 'from_manager_id', label: 'Current Reporting Manager' },
          { name: 'to_manager_id', label: 'Destination Reporting Manager' }
        ]
      },

      // ================= TAB 3: COMPENSATION & PAYROLL =================
      {
        tab: 'compensation',
        title: 'Basic Salary & Monthly Emoluments',
        note: 'Current vs proposed basic wages and monthly gross salary structuring.',
        fields: [
          { name: 'current_basic', label: 'Current Basic Salary' },
          { name: 'proposed_basic', label: 'Proposed Basic Salary' },
          { name: 'basic_increment_pct', label: 'Increment Percentage' },
          { name: 'current_gross', label: 'Current Monthly Gross' },
          { name: 'proposed_gross', label: 'Proposed Monthly Gross' }
        ]
      },
      {
        tab: 'compensation',
        title: 'Statutory Allowances & Tax Jurisdiction',
        note: 'House rent, medical, conveyance, skill allowances, and NBR tax zone minimums.',
        fields: [
          { name: 'proposed_house_rent', label: 'Proposed House Rent Allowance' },
          { name: 'proposed_medical', label: 'Proposed Medical Allowance' },
          { name: 'proposed_conveyance', label: 'Proposed Conveyance Allowance' },
          { name: 'proposed_skill_allowance', label: 'Proposed Technical Skill Allowance' },
          { name: 'deputation_allowance', label: 'Deputation Allowance' },
          { name: 'to_tax_location', label: 'Destination Tax Jurisdiction' },
          { name: 'effective_payroll_month', label: 'Effective Payroll Month (YYYY-MM)' }
        ]
      },

      // ================= TAB 4: TECHNICAL & OEM BADGES =================
      {
        tab: 'technical',
        title: 'Repair Competency & Technical Accreditations',
        note: 'After-sales repair tier competency, OEM brand authorizations, and technical board scores.',
        fields: [
          { name: 'from_repair_tier', label: 'Current Repair Tier' },
          { name: 'to_repair_tier', label: 'Assigned Technical Repair Tier' },
          { name: 'oem_brand_authorizations', label: 'OEM Brand Authorizations' },
          { name: 'technical_assessment_score', label: 'Technical Assessment Score (0-100)' },
          { name: 'technical_evaluator_id', label: 'Technical Evaluator' }
        ]
      },
      {
        tab: 'technical',
        title: 'Safety, Lab Facilities & Governance',
        note: 'ESD workstation calibration, BGA machine operator license, and customer NDA signoff.',
        fields: [
          { name: 'target_workbench_id', label: 'Destination Workbench Station ID' },
          { name: 'esd_certified', label: 'ESD Safety Certified & Calibrated' },
          { name: 'bga_license', label: 'BGA Rework Machine Operator License' },
          { name: 'target_dispatch_zone', label: 'GPS Field Dispatch Zone' },
          { name: 'nda_confirmed', label: 'Customer Data Privacy Undertaking Confirmed' }
        ]
      },

      // ================= TAB 5: HANDOVER & CUSTODY CLEARANCE =================
      {
        tab: 'handover',
        title: 'Customer RMA & Open Job Card Clearance',
        note: 'Reconciliation and transfer of open repair tickets to prevent customer SLA breach.',
        fields: [
          { name: 'open_jobs_audited', label: 'Open Customer Service Orders Audited', readonly: true },
          { name: 'open_jobs_transferred_count', label: 'Open RMA / Job Cards Transferred Count' },
          { name: 'open_jobs_reassignment_ref', label: 'Open Jobs Reassignment Docket Ref' }
        ]
      },
      {
        tab: 'handover',
        title: 'Tool Kit Custody & Equipment Reconciliation',
        note: 'Return of micro-soldering stations, oscilloscopes, and specialized tool kits.',
        fields: [
          { name: 'toolkit_custody_ref', label: 'Tool Kit Custody Inventory Tag Ref' },
          { name: 'toolkit_returned', label: 'Micro-soldering Tool Kit Returned', readonly: true },
          { name: 'toolkit_challan_no', label: 'Tool Kit Return Challan Number' }
        ]
      },
      {
        tab: 'handover',
        title: 'Spare Parts & Accounts Clearance',
        note: 'Van stock spare parts inventory reconciliation and branch imprest settlement.',
        fields: [
          { name: 'spare_parts_reconciled', label: 'Transit Spare Parts Reconciled', readonly: true },
          { name: 'spare_parts_variance_value', label: 'Transit Spare Parts Discrepancy Value' },
          { name: 'clearance_mrn_no', label: 'Material Return Note (MRN) Number' },
          { name: 'storekeeper_cleared', label: 'Branch Storekeeper Clearance Signed', readonly: true },
          { name: 'storekeeper_id', label: 'Origin Branch Storekeeper' },
          { name: 'imprest_cash_settled', label: 'Branch Imprest Cash Settled', readonly: true }
        ]
      },

      // ================= TAB 6: RELOCATION & TRANSIT LEAVE =================
      {
        tab: 'logistics',
        title: 'Relocation Financial Assistance',
        note: 'Transfer grants, disturbance allowance, and moving transport allowances.',
        fields: [
          { name: 'transfer_grant', label: 'Transfer Grant / Disturbance Allowance' },
          { name: 'luggage_allowance', label: 'Luggage & Packing Transport Allowance' },
          { name: 'travel_allowance', label: 'Travel Allowance TA/DA' }
        ]
      },
      {
        tab: 'logistics',
        title: 'Transit Leave & Transit Accommodation',
        note: 'Paid statutory transit leave under BLA Rule 22 and station joining schedule.',
        fields: [
          { name: 'transit_leave_days', label: 'Paid Transit Leave Days (BLA Rule 22)' },
          { name: 'transit_start_date', label: 'Transit Leave Start Date' },
          { name: 'transit_end_date', label: 'Transit Leave End Date' },
          { name: 'shifting_vendor', label: 'Household Moving Vendor Name' },
          { name: 'temporary_stay_provided', label: 'Company Transit Accommodation Provided' },
          { name: 'destination_joining_date', label: 'Actual Station Joining Date' }
        ]
      },

      // ================= TAB 7: AUTHORIZATION WORKFLOW =================
      {
        tab: 'approval',
        title: 'Branch & Operational Recommendation',
        note: 'Recommendation and concurrence signoffs by releasing and receiving branch heads.',
        fields: [
          { name: 'origin_manager_approval', label: 'Origin Branch Recommendation', readonly: true },
          { name: 'origin_manager_id', label: 'Origin Recommending Manager', readonly: true },
          { name: 'origin_manager_date', label: 'Recommendation Date', readonly: true },
          { name: 'destination_manager_approval', label: 'Destination Branch Concurrence', readonly: true },
          { name: 'destination_manager_id', label: 'Destination Receiving Manager', readonly: true },
          { name: 'destination_manager_date', label: 'Concurrence Date', readonly: true }
        ]
      },
      {
        tab: 'approval',
        title: 'Technical, Compliance & Executive Signoff',
        note: 'Multi-tier verification by Technical Board, HR Audit, Finance CFO, and Executive MD.',
        fields: [
          { name: 'tech_head_approval', label: 'Technical Board Evaluation', readonly: true },
          { name: 'tech_head_id', label: 'Technical Evaluation Head', readonly: true },
          { name: 'tech_head_date', label: 'Technical Signoff Date', readonly: true },
          { name: 'hr_head_approval', label: 'HR Compliance & Legal Audit', readonly: true },
          { name: 'hr_head_id', label: 'HR Operations Lead', readonly: true },
          { name: 'hr_head_date', label: 'HR Audit Date', readonly: true },
          { name: 'finance_head_approval', label: 'Finance & Budget Clearance', readonly: true },
          { name: 'finance_head_id', label: 'Financial Controller', readonly: true },
          { name: 'finance_head_date', label: 'Finance Clearance Date', readonly: true },
          { name: 'executive_approval', label: 'Executive Management Approval', readonly: true },
          { name: 'executive_id', label: 'Managing Director / Executive Head', readonly: true },
          { name: 'executive_date', label: 'Executive Signoff Date', readonly: true },
          { name: 'rejection_reason', label: 'Rejection or Audit Discrepancy Remarks', readonly: true }
        ]
      },

      // ================= TAB 8: DOCUMENT VAULT =================
      {
        tab: 'vault',
        title: 'Official Movement Orders & Labour Compliance',
        note: 'Scanned physical transfer order, Form 7 service book endorsement, and contract addendum.',
        fields: [
          { name: 'transfer_letter_file', label: 'Official Transfer / Promotion Order Scan', type: 'file' },
          { name: 'service_book_endorsement_file', label: 'Form 7 Service Book Endorsement Scan', type: 'file' },
          { name: 'contract_addendum_file', label: 'Amended Contract Addendum Scan', type: 'file' }
        ]
      },
      {
        tab: 'vault',
        title: 'Operational Handover & Reconciliation Scans',
        note: 'Signed tool kit return challan, spare parts MRN, customer job docket, and joining report.',
        fields: [
          { name: 'handover_challan_file', label: 'Tool Kit Custody Return Challan', type: 'file' },
          { name: 'clearance_mrn_file', label: 'Spare Parts Clearance MRN Scan', type: 'file' },
          { name: 'open_jobs_docket_file', label: 'Open Job Card Reassignment Docket Scan', type: 'file' },
          { name: 'joining_report_file', label: 'Station Joining Report Scan', type: 'file' }
        ]
      }
    ]
  },

  'M21-form-exit': {
    kind: 'model_form',
    model: 'fix.hr.exit',
    title: 'Exit & Final Settlement',
    back: 'M21-exit',
    status: { field: 'state', labels: {
      draft: 'Draft', notice: 'Notice Confirmed', cleared: 'Cleared', settled: 'Settled', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'separation', label: 'Separation Notice', bn: 'প্রস্থান নোটিশ', icon: '🚪', badge: '6' },
      { id: 'clearance', label: 'Clearance Checklist', bn: 'ছাড়পত্র যাচাই', icon: '📋', badge: '4' },
      { id: 'settlement', label: 'Final Settlement', bn: 'চূড়ান্ত নিষ্পত্তি', icon: '💰', badge: '3' }
    ],
    sections: [
      {
        tab: 'separation',
        title: 'Separation Particulars',
        note: 'Resignation, termination, or retirement details under BLA 2006 Chapter II.',
        fields: [
          { name: 'name', label: 'Exit Reference', readonly: true },
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'exit_type', required: true, label: 'Exit Type' },
          { name: 'notice_date', label: 'Notice Submission Date' },
          { name: 'notice_required_days', label: 'Statutory Notice (days)', readonly: true },
          { name: 'notice_served_days', label: 'Notice Served (days)', readonly: true },
          { name: 'notice_basis', label: 'Statutory Basis', readonly: true },
          { name: 'notice_shortfall_treatment', label: 'Notice Shortfall Treatment' },
          { name: 'chief_inspector_notified_on', label: 'Retrenchment: Chief Inspector / CBA Copy Sent' },
          { name: 'disciplinary_case_id', label: 'Disciplinary Case (dismissal)' },
          { name: 'abandonment_id', label: 'Absence Case (s.27(3A))', readonly: true },
          { name: 'death_at_work', label: 'Death at Work / Work Accident (s.19: 45 days)' },
          { name: 'death_certificate_file', label: 'Death Certificate', type: 'file' },
          { name: 'last_working_day', required: true, label: 'Last Working Day (date of death for s.19)' },
          { name: 'reason', label: 'Separation Reason' },
          { name: 'state', required: true, label: 'Workflow State', readonly: true }
        ]
      },
      {
        tab: 'clearance',
        title: 'Departmental Clearance Checklist',
        note: 'All clearance gates and physical asset return receipt must be signed off before processing final separation wages.',
        fields: [
          { name: 'clearance_it', label: 'IT Assets & System Access Deprovisioned', readonly: true },
          { name: 'clearance_finance', label: 'Finance & Advances Dues Cleared', readonly: true },
          { name: 'clearance_hr', label: 'HR Documents & Service Book Handed Over', readonly: true },
          { name: 'clearance_assets', label: 'Physical Tools & Uniform Returned', readonly: true },
          { name: 'asset_return_receipt_no', label: 'Asset Return Receipt / MRN No' },
          { name: 'asset_return_receipt_file', label: 'Signed Asset Return Receipt Scan', type: 'file' }
        ]
      },
      {
        tab: 'settlement',
        title: 'Final Settlement & Gratuity Calculation',
        note: 'Gratuity, unavailed earned leave encashment (s. 118) and final salary dues.',
        fields: [
          { name: 'settlement_amount', label: 'Total Net Settlement Amount (BDT, computed by payroll)', readonly: true },
          { name: 'settlement_basis', label: 'Settlement Basis (payroll)', readonly: true },
          { name: 'settlement_due_date', label: 'Dues Payable By (s.30 / s.123(2))', readonly: true },
          { name: 'settlement_overdue', label: 'Settlement Overdue', readonly: true },
          { name: 'approval_state', label: 'Finance Approval (M63)', readonly: true },
          { name: 'settled_on', label: 'Settled On', readonly: true },
          { name: 'nominee_payout_lines', label: 'Nominee Split (s.19, pinned)', readonly: true },
          { name: 'service_certificate_id', label: 'Service Certificate (s.31)', readonly: true },
          { name: 'currency_id', label: 'Currency' }
        ]
      }
    ]
  },

  'M21-form-document': {
    kind: 'model_form',
    model: 'fix.hr.document',
    title: 'Statutory Document',
    back: 'M21-appointment',
    tabs: [
      { id: 'document', label: 'Document Particulars', bn: 'নথির বিবরণ', icon: '📄', badge: '5' },
      { id: 'file', label: 'Physical Document Scan', bn: 'কাগজপত্রের স্ক্যান ফাইল', icon: '📎', badge: '3' },
      { id: 'verification', label: 'Compliance & Verification', bn: 'যাচাই ও সম্মতি', icon: '✅', badge: '2' }
    ],
    sections: [
      {
        tab: 'document',
        title: 'Statutory Record Particulars',
        note: 'Document classification, employee link, and validity duration under BLA 2006.',
        fields: [
          { name: 'name', label: 'Document Reference No' },
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'doc_type', required: true, label: 'Document Classification' },
          { name: 'reference', label: 'Issuing Authority Reference' },
          { name: 'issued_on', label: 'Date of Issue' },
          { name: 'expiry_date', label: 'Expiry Date' }
        ]
      },
      {
        tab: 'file',
        title: 'Physical Scanned Document Attachment',
        note: 'Upload digital scan of physical paper document (PDF, JPG, PNG, DOCX up to 10MB).',
        fields: [
          { name: 'file_data', label: 'Physical Document File (PDF / Scan)', type: 'file' },
          { name: 'file_name', label: 'Attached Filename' },
          { name: 'notes', label: 'Dossier Notes & Custody Details' }
        ]
      },
      {
        tab: 'verification',
        title: 'Audit Verification & Employee Acknowledgement',
        note: 'Statutory verification signoff under Bangladesh Labour Act 2006.',
        fields: [
          { name: 'verified', label: 'Verified by HR Compliance', readonly: true },
          { name: 'acknowledged', label: 'Acknowledged by Employee', readonly: true }
        ]
      }
    ]
  },

  'M21-form-dependant': {
    kind: 'model_form',
    model: 'fix.hr.dependant',
    title: 'Dependant / Nominee',
    back: 'M21-nominees',
    tabs: [
      { id: 'identity', label: 'Dependant Identity', bn: 'মনোনীত ব্যক্তির পরিচয়', icon: '👨‍👩‍👧', badge: '5' },
      { id: 'entitlement', label: 'Nominee Share (BLA s.19)', bn: 'মনোনয়নের অংশ', icon: '⚖️', badge: '2' }
    ],
    sections: [
      {
        tab: 'identity',
        title: 'Dependant & Family Member Particulars',
        note: 'Legal identity and relationship of dependant or statutory nominee.',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'name', required: true, label: 'Full Legal Name' },
          { name: 'relation', required: true, label: 'Relationship' },
          { name: 'date_of_birth', label: 'Date of Birth' },
          { name: 'nid', label: 'NID / Birth Registration No' }
        ]
      },
      {
        tab: 'entitlement',
        title: 'Statutory Nominee Share Allocation',
        note: 'Nominee share is a 0–100 percentage under BLA 2006 s.19 & s.131.',
        fields: [
          { name: 'is_nominee', label: 'Designated Statutory Nominee' },
          { name: 'nominee_pct', label: 'Nominee Share %' }
        ]
      }
    ]
  },


  /* ===== master-data forms (batch 2) — D365 in-workspace ===== */
  'M21-form-position': {
    kind: 'model_form',
    model: 'fix.org.position',
    title: "Organisation Position",
    back: 'M21-positions',
    tabs: [
      { id: 'seat', label: 'Establishment Seat', bn: 'পদ ও কাঠামো', icon: '🏢', badge: '3' },
      { id: 'hierarchy', label: 'Reporting & Scope', bn: 'রিপোর্টিং ও শাখা', icon: '🗂️', badge: '2' }
    ],
    sections: [
      {
        tab: 'seat',
        title: "Organisation Establishment Position",
        note: "A sanctioned seat in the organisation chart; headcount and approval routing hang off it.",
        fields: [
          { name: 'company_id', required: true, label: "Company" },
          { name: 'name', required: true, label: "Position Title" },
          { name: 'grade', label: "Corporate Grade / Band" },
          { name: 'headcount', label: "Sanctioned Headcount (no dual occupancy beyond it)" }
        ]
      },
      {
        tab: 'hierarchy',
        title: "Reporting Line & Operating Unit",
        note: "Direct reporting position and branch operating unit.",
        fields: [
          { name: 'parent_id', label: "Reports To Position" },
          { name: 'operating_unit_id', label: "Operating Unit" }
        ]
      }
    ]
  },


  /* ===== triage coverage screens ===== */
  'M21-leave-type': { kind: 'model_list', model: 'fix.leave.type',
    cols: ['name', 'code', 'company_id', 'operating_unit_id', 'name_bn', 'entitlement_days', 'encashable'] },

  'M21-form-leave-type': {
    kind: 'model_form',
    model: 'fix.leave.type',
    title: "Leave Type",
    back: 'M21-leave-type',
    tabs: [
      { id: 'definition', label: 'Leave Definition', bn: 'ছুটির সংজ্ঞা', icon: '🌴', badge: '4' },
      { id: 'policy', label: 'Entitlement & Encashment', bn: 'প্রাপ্যতা ও নগদায়ন', icon: '⚖️', badge: '3' }
    ],
    sections: [
      {
        tab: 'definition',
        title: "Statutory Leave Classification",
        note: "Leave categories under Bangladesh Labour Act 2006 (Casual s.115, Sick s.116, Annual Earned s.117, Festival s.118).",
        fields: [
          { name: 'name', required: true, label: "Leave Name (English)" },
          { name: 'name_bn', label: "Leave Name (Bengali)" },
          { name: 'code', required: true, label: "Leave Code" },
          { name: 'company_id', required: true, label: "Company" }
        ]
      },
      {
        tab: 'policy',
        title: "Annual Quota & Encashment Rules",
        note: "Statutory annual day entitlement and encashability at year-end or separation.",
        fields: [
          { name: 'entitlement_days', required: true, label: "Annual Entitlement Days" },
          { name: 'encashable', label: "Encashable Under BLA s.117" },
          { name: 'operating_unit_id', label: "Operating Unit" }
        ]
      }
    ]
  },

  'M21-education': { kind: 'model_list', model: 'fix.hr.education',
    cols: ['employee_id', 'degree_level', 'degree_title', 'major_group', 'board_university', 'passing_year', 'gpa_score', 'is_verified'],
    actions: [
      { m: 'action_verify_online', l: 'Verified Online (second person)' },
      { m: 'action_verify_physical', l: 'Verified Physical Certificate' },
      { m: 'action_flag_discrepancy', l: 'Flag Discrepancy' }
    ] },
  'M21-experience': { kind: 'model_list', model: 'fix.hr.experience',
    cols: ['employee_id', 'company_name', 'industry_type', 'designation_held', 'start_date', 'end_date', 'experience_years', 'reference_status'],
    actions: [
      { m: 'action_reference_positive', l: 'Reference: Positive' },
      { m: 'action_reference_neutral', l: 'Reference: Neutral' },
      { m: 'action_reference_negative', l: 'Reference: Negative' },
      { m: 'action_reference_unreachable', l: 'Reference: Unreachable' }
    ] },

  /* A09 P0-b: the sensitive master change (bank, MFS, NID, e-TIN) and the
   * disciplinary case. Their surfaces join controllers/a09/m21.py once the
   * write whitelist is regenerated (coordinator). */
  'M21-master-change': { kind: 'model_list', model: 'fix.hr.master.change', stateField: 'state',
    cols: ['name', 'employee_id', 'reason', 'approval_state', 'state'],
    actions: [
      { m: 'action_submit', l: 'Submit for Approval', states: ['draft'] },
      { m: 'action_cancel', l: 'Cancel', states: ['draft', 'submitted'] }
    ] },
  'M21-disciplinary': { kind: 'model_list', model: 'fix.hr.disciplinary.case', stateField: 'state',
    cols: ['name', 'employee_id', 'misconduct_category', 'charge_date', 'explanation_due', 'enquiry_due', 'suspended', 'outcome', 'state'],
    actions: [
      { m: 'action_charge', l: 'Serve Charge', states: ['draft'] },
      { m: 'action_record_explanation', l: 'Record Explanation', states: ['charged'] },
      { m: 'action_hold_hearing', l: 'Hold Hearing', states: ['charged', 'explained'] },
      { m: 'action_start_enquiry', l: 'Start Enquiry', states: ['hearing'] },
      { m: 'action_conclude_enquiry', l: 'Conclude Enquiry', states: ['enquiry'] },
      { m: 'action_request_approval', l: 'Request Decision', states: ['concluded'] },
      { m: 'action_suspend', l: 'Suspend (max 60 days)', states: ['charged', 'explained', 'hearing', 'enquiry'] },
      { m: 'action_end_suspension', l: 'End Suspension' },
      { m: 'action_withdraw', l: 'Withdraw Case' }
    ] },
  'M21-form-master-change': {
    kind: 'model_form',
    model: 'fix.hr.master.change',
    title: 'Employee Master Change',
    back: 'M21-master-change',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Submitted', applied: 'Applied', rejected: 'Rejected', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'request', label: 'Request', bn: 'অনুরোধ', icon: '📝', badge: '3' },
      { id: 'banking', label: 'Bank & MFS', bn: 'ব্যাংক ও এমএফএস', icon: '🏦', badge: '6' },
      { id: 'identity', label: 'Identity & Eligibility', bn: 'পরিচয় ও যোগ্যতা', icon: '🪪', badge: '3' }
    ],
    sections: [
      {
        tab: 'request',
        title: 'Change Request',
        note: 'Maker-checker (FR-HCM-042): another HR officer decides it from the approval inbox; the requester and the employee never do.',
        fields: [
          { name: 'name', label: 'Reference', readonly: true },
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'reason', required: true, label: 'Reason for the Change' },
          { name: 'evidence_file', label: 'Evidence (cheque leaf, NID, TIN)', type: 'file' },
          { name: 'approval_state', label: 'Approval (M63)', readonly: true },
          { name: 'state', label: 'State', readonly: true }
        ]
      },
      {
        tab: 'banking',
        title: 'Proposed Salary Channel',
        note: 'BEFTN routing 9 digits; MFS 01XXXXXXXXX. Leave a field empty to keep it.',
        fields: [
          { name: 'proposed_bank_name', label: 'Bank Name' },
          { name: 'proposed_bank_branch_name', label: 'Branch' },
          { name: 'proposed_routing_number', label: 'BEFTN Routing (9 digits)' },
          { name: 'proposed_bank_account_number', label: 'Bank Account Number' },
          { name: 'proposed_mfs_provider', label: 'MFS Provider' },
          { name: 'proposed_mfs_account_number', label: 'MFS Wallet Number' }
        ]
      },
      {
        tab: 'identity',
        title: 'Proposed Identity & Eligibility',
        note: 'NID 10, 13 or 17 digits; e-TIN 12 digits; overtime eligibility under BLA s.108.',
        fields: [
          { name: 'proposed_nid_number', label: 'NID' },
          { name: 'proposed_tin_number', label: 'e-TIN' },
          { name: 'proposed_overtime_eligible', label: 'Overtime Eligibility' }
        ]
      }
    ]
  },
  'M21-form-abandonment': {
    kind: 'model_form',
    model: 'fix.hr.abandonment',
    title: 'Absence Without Leave (BLA s.27(3A))',
    back: 'M21-abandonment',
    status: { field: 'state', labels: {
      draft: 'Draft', noticed: 'Notice Served', hearing: 'Self-Defence Window', decision: 'Awaiting Decision',
      deemed: 'Deemed Resigned', explained: 'Explained / Rejoined', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'absence', label: 'Absence & Notices', bn: 'অনুপস্থিতি ও নোটিশ', icon: '📅', badge: '9' },
      { id: 'decision', label: 'Explanation & Decision', bn: 'জবাব ও সিদ্ধান্ত', icon: '⚖️', badge: '7' }
    ],
    sections: [
      {
        tab: 'absence',
        title: 'Absence and the s.27(3A) Timeline',
        note: 'More than 10 days absent without leave: a notice gives 10 days to explain or rejoin, then 7 more days for self-defence (company settings).',
        fields: [
          { name: 'name', label: 'Case Reference', readonly: true },
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'absence_start_date', required: true, label: 'First Day of Absence' },
          { name: 'absent_days', label: 'Days Absent', readonly: true },
          { name: 'notes', label: 'Attempts to Contact' },
          { name: 'notice_date', label: 'Notice Served On', readonly: true },
          { name: 'reply_due', label: 'Explanation Due', readonly: true },
          { name: 'hearing_notice_date', label: 'Second Notice On', readonly: true },
          { name: 'hearing_due', label: 'Self-Defence Due', readonly: true }
        ]
      },
      {
        tab: 'decision',
        title: 'Explanation and the Routed Decision',
        note: 'The deemed resignation is decided from the executive approval inbox; the case officer and the worker never decide it. It opens the abandonment exit.',
        fields: [
          { name: 'explanation', label: 'Worker Explanation / Rejoining' },
          { name: 'explanation_received_on', label: 'Explanation Received On', readonly: true },
          { name: 'approval_state', label: 'Decision Approval (M63)', readonly: true },
          { name: 'decided_by_id', label: 'Decided By', readonly: true },
          { name: 'decided_on', label: 'Decided On', readonly: true },
          { name: 'exit_id', label: 'Exit Opened', readonly: true },
          { name: 'state', label: 'State', readonly: true }
        ]
      }
    ]
  },
  'M21-form-disciplinary': {
    kind: 'model_form',
    model: 'fix.hr.disciplinary.case',
    title: 'Disciplinary Case (BLA s.23/24)',
    back: 'M21-disciplinary',
    status: { field: 'state', labels: {
      draft: 'Draft', charged: 'Charge Served', explained: 'Explanation Received', hearing: 'Hearing Held',
      enquiry: 'Enquiry', concluded: 'Enquiry Concluded', decided: 'Decided', cancelled: 'Withdrawn' } },
    tabs: [
      { id: 'charge', label: 'Charge & Explanation', bn: 'অভিযোগ ও জবাব', icon: '📄', badge: '7' },
      { id: 'enquiry', label: 'Hearing & Enquiry', bn: 'শুনানি ও তদন্ত', icon: '⚖️', badge: '7' },
      { id: 'decision', label: 'Decision & Suspension', bn: 'সিদ্ধান্ত ও সাময়িক বরখাস্ত', icon: '✍️', badge: '9' }
    ],
    sections: [
      {
        tab: 'charge',
        title: 'Written Charge (s.24)',
        note: 'The worker has at least 7 days to explain before the hearing.',
        fields: [
          { name: 'name', label: 'Case Reference', readonly: true },
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'misconduct_category', required: true, label: 'Misconduct (s.23(4))' },
          { name: 'allegation', required: true, label: 'Written Allegation' },
          { name: 'charge_date', label: 'Charge Served On' },
          { name: 'reply_days', label: 'Days to Explain (minimum 7)' },
          { name: 'explanation_due', label: 'Explanation Due', readonly: true },
          { name: 'explanation', label: "Worker's Explanation" },
          { name: 'explanation_received_on', label: 'Explanation Received On' }
        ]
      },
      {
        tab: 'enquiry',
        title: 'Hearing & Enquiry Committee',
        note: 'Equal employer and worker representatives; the enquiry concludes within 60 days.',
        fields: [
          { name: 'hearing_date', label: 'Hearing Date' },
          { name: 'hearing_notes', label: 'Hearing Notes' },
          { name: 'employer_rep_ids', label: 'Employer Representatives' },
          { name: 'worker_rep_ids', label: 'Worker Representatives' },
          { name: 'enquiry_started_on', label: 'Enquiry Started', readonly: true },
          { name: 'enquiry_due', label: 'Enquiry Due (60 days)', readonly: true },
          { name: 'findings', label: 'Findings' },
          { name: 'proposed_outcome', label: 'Proposed Outcome' }
        ]
      },
      {
        tab: 'decision',
        title: 'Decision & Suspension',
        note: 'The decision is the employer approver\'s (approval inbox). Suspension pending enquiry lasts at most 60 days.',
        fields: [
          { name: 'approval_state', label: 'Decision Approval (M63)', readonly: true },
          { name: 'outcome', label: 'Outcome', readonly: true },
          { name: 'decided_by_id', label: 'Decided By', readonly: true },
          { name: 'decided_on', label: 'Decided On', readonly: true },
          { name: 'suspended', label: 'Suspended', readonly: true },
          { name: 'suspended_from', label: 'Suspended From', readonly: true },
          { name: 'suspended_until', label: 'Suspended Until', readonly: true },
          { name: 'subsistence_pct', label: 'Subsistence Allowance %', readonly: true },
          { name: 'state', label: 'State', readonly: true }
        ]
      }
    ]
  },
  'M21-form-education': {
    kind: 'model_form',
    model: 'fix.hr.education',
    title: 'Academic Qualification',
    back: 'M21-education',
    tabs: [
      { id: 'credential', label: 'Academic Credential', bn: 'সনদ ও ডিগ্রি', icon: '🎓' },
      { id: 'audit', label: 'Registration & Verification', bn: 'রেজিস্ট্রেশন ও যাচাই', icon: '📑' }
    ],
    sections: [
      {
        tab: 'credential',
        title: 'Academic Qualification Details',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'degree_level', required: true, label: 'Education Level' },
          { name: 'degree_title', required: true, label: 'Degree Title' },
          { name: 'major_group', required: true, label: 'Field / Major' },
          { name: 'board_university', required: true, label: 'Board / University' },
          { name: 'institute_name', label: 'Institution Name' }
        ]
      },
      {
        tab: 'audit',
        title: 'Examination Result & Verification Audit',
        fields: [
          { name: 'passing_year', required: true, label: 'Passing Year' },
          { name: 'result_type', label: 'Grading System' },
          { name: 'gpa_score', required: true, label: 'GPA / Score' },
          { name: 'roll_number', label: 'Roll Number' },
          { name: 'registration_no', label: 'Registration Number' },
          { name: 'is_verified', label: 'Verification Status', readonly: true },
          { name: 'certificate_file', label: 'Academic Certificate (Scanned File)', type: 'file' },
          { name: 'certificate_filename', label: 'Certificate Filename' }
        ]
      }
    ]
  },
  'M21-form-experience': {
    kind: 'model_form',
    model: 'fix.hr.experience',
    title: 'Work Experience',
    back: 'M21-experience',
    tabs: [
      { id: 'employment', label: 'Employment Scope', bn: 'প্রতিষ্ঠানের বিবরণ', icon: '💼' },
      { id: 'reference', label: 'Compensation & Reference', bn: 'বেতন ও রেফারেন্স', icon: '⚖️' }
    ],
    sections: [
      {
        tab: 'employment',
        title: 'Previous Organization Details',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'company_name', required: true, label: 'Previous Company Name' },
          { name: 'industry_type', label: 'Industry Sector' },
          { name: 'designation_held', required: true, label: 'Designation Held' },
          { name: 'start_date', required: true, label: 'Start Date' },
          { name: 'end_date', required: true, label: 'End Date' }
        ]
      },
      {
        tab: 'reference',
        title: 'Compensation, Separation & Reference Check',
        fields: [
          { name: 'last_drawn_salary', label: 'Last Drawn Salary (BDT)' },
          { name: 'reason_for_leaving', label: 'Separation Reason' },
          { name: 'supervisor_name', label: 'Supervisor Name' },
          { name: 'supervisor_phone', label: 'Supervisor Phone' },
          { name: 'reference_status', label: 'Reference Verification Status', readonly: true },
          { name: 'experience_letter_file', label: 'Experience / Release Letter (Scanned File)', type: 'file' },
          { name: 'experience_letter_filename', label: 'Release Letter Filename' }
        ]
      }
    ]
  },
};

export const REPORT_ROUTES = {
  'M21:Headcount & Movement': 'M21-rpt-headcount',
  'M21:Attrition Analysis': 'M21-rpt-attrition',
  'M21:Probation Conversion': 'M21-rpt-probation',
  'M21:Establishment Register': 'M21-rpt-establishment',
  'M21:Form 6(a) Register': 'M21-rpt-form6a',
  'M21:Identity Read Log': 'M21-rpt-identity-log',
  'M21:Data Clean-up Findings': 'M21-rpt-cleanup',
  'M21:Org Distribution': 'M21-orgchart'
};

export const FORM_MODELS = {
  'M21:Employee': 'hr.employee',
  'M21:Transfer': 'fix.hr.transfer',
  'M21:Promotion': 'fix.hr.transfer',
  'M21:Exit Clearance': 'fix.hr.exit',
  'M21:Education': 'fix.hr.education',
  'M21:Experience': 'fix.hr.experience'
};

export const FORM_CHIPS = {
  'M21:Organisation Position': 'M21-form-position',
  'M21:Employee': 'M21-employee',
  'M21:Transfer': 'M21-form-transfer',
  'M21:Promotion': 'M21-form-transfer',
  'M21:Exit Clearance': 'M21-form-exit',
  'M21:Education': 'M21-form-education',
  'M21:Experience': 'M21-form-experience',
  'M21:__by_model__': {
    'fix.leave.type': 'M21-form-leave-type',
    'fix.org.position': 'M21-form-position',
    'hr.employee': 'M21-employee',
    'fix.employment.contract': 'M21-form-contract',
    'fix.hr.transfer': 'M21-form-transfer',
    'fix.hr.exit': 'M21-form-exit',
    'fix.hr.document': 'M21-form-document',
    'fix.hr.dependant': 'M21-form-dependant',
    'fix.hr.education': 'M21-form-education',
    'fix.hr.experience': 'M21-form-experience',
    'fix.hr.master.change': 'M21-form-master-change',
    'fix.hr.disciplinary.case': 'M21-form-disciplinary',
    'fix.hr.abandonment': 'M21-form-abandonment'
  },
  'M21:__by_screen__': {
    'M21-leave-type': 'M21-form-leave-type',
    'M21-positions': 'M21-form-position',
    'M21-directory': 'M21-employee',
    'M21-hire': 'M21-form-contract',
    'M21-transfer': 'M21-form-transfer',
    'M21-exit': 'M21-form-exit',
    'M21-appointment': 'M21-form-document',
    'M21-servicebook': 'M21-form-document',
    'M21-nominees': 'M21-form-dependant',
    'M21-education': 'M21-form-education',
    'M21-experience': 'M21-form-experience',
    'M21-master-change': 'M21-form-master-change',
    'M21-disciplinary': 'M21-form-disciplinary',
    'M21-abandonment': 'M21-form-abandonment'
  }
};

export const CREATE = {
  M21: { screen: 'M21-employee', model: 'hr.employee', label: 'Employee' }
};
