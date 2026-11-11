/** @odoo-module **/
/* A09 · People & Workforce — M55 Time, Attendance & Scheduling.
 * Registry-faithful: 4 groups / 13 screens / 5 reports / 4 forms / freg 74 (A09 P0-b adds
 * overtime requests, regularisation decisions, night-work consent, accrual, balances; A09 r2
 * adds the webhook log, biometric consent, roster publication and change control, the
 * working-time rule versions and the forward adjustments to payroll). */

export const MODULE = {
  area: 'A09', code: 'M55', en: 'Time, Attendance & Scheduling', title: 'M55 · Time, Attendance & Scheduling',
  bn: 'সময়, উপস্থিতি ও শিডিউলিং', icon: '⏰',
  desc: 'Biometric and geofenced capture, exception regularisation, working-time rules and overtime, moon-dependent holidays, leave requests and balances, shift patterns, rosters and publication, on-call standby, and availability published to dispatch.',
  kpis: [
    { l: 'Attendance Today', m: 'attendance_today' },
    { l: 'Exceptions Pending', m: 'exceptions_pending' },
    { l: 'Overtime Requests Approved (month)', m: 'overtime_preapproved' },
    { l: 'Roster Coverage', m: 'roster_coverage', suffix: '%' },
    { l: 'Leave Pending', m: 'leave_pending' },
    { l: 'Geofence Clock-Ins', m: 'geofence_clockins' },
    { l: 'Rosters Awaiting Publication', m: 'rosters_awaiting' },
    { l: 'Adjustments Awaiting Approval', m: 'adjustments_open' }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M55-attendance-lock', en: "Attendance Lock", bn: "উপস্থিতি লক", t: 'g' }
    ]},
    { en: 'Capture', screens: [
      { id: 'M55-daily', en: 'Daily Attendance', bn: 'দৈনিক উপস্থিতি', t: 'g' },
      { id: 'M55-devices', en: 'Biometric Devices', bn: 'বায়োমেট্রিক', t: 'g' },
      { id: 'M55-hook-events', en: 'Device Webhook Events', bn: 'ডিভাইস ইভেন্ট', t: 'g' },
      { id: 'M55-bio-consent', en: 'Biometric Consent (PDPA)', bn: 'বায়োমেট্রিক সম্মতি', t: 'g' },
      { id: 'M55-geofence', en: 'Geofenced Clock-In', bn: 'জিওফেন্স', t: 'g' },
      { id: 'M55-exc', en: 'Exception Regularisation', bn: 'ব্যতিক্রম নিয়মিতকরণ', t: 'g' },
      { id: 'M55-regs', en: 'Regularisation Decisions', bn: 'নিয়মিতকরণ সিদ্ধান্ত', t: 'g' }
    ]},
    { en: 'Working Time', screens: [
      { id: 'M55-rules', en: 'Rules & Overtime', bn: 'নিয়ম ও অতিরিক্ত সময়', t: 'r' },
      { id: 'M55-wt-rules', en: 'Working-Time Rule Versions', bn: 'কর্মঘণ্টা নিয়ম সংস্করণ', t: 'g' },
      { id: 'M55-adjustments', en: 'Forward Adjustments (to Payroll)', bn: 'পরবর্তী সমন্বয়', t: 'g' },
      { id: 'M55-ot', en: 'Overtime Requests', bn: 'অতিরিক্ত সময়ের আবেদন', t: 'g' },
      { id: 'M55-night', en: 'Night-Work Consent (s.109)', bn: 'রাত্রিকালীন কাজের সম্মতি', t: 'g' },
      { id: 'M55-holidays', en: 'Holidays (moon-dependent)', bn: 'ছুটির দিনপঞ্জি', t: 'g' }
    ]},
    { en: 'Leave', screens: [
      { id: 'M55-leave', en: 'Leave Requests', bn: 'ছুটির আবেদন', t: 'g' },
      { id: 'M55-balances', en: 'Balances', bn: 'ব্যালান্স', t: 'r' },
      { id: 'M55-accrual', en: 'Annual Leave Accrual (s.117)', bn: 'অর্জিত ছুটি', t: 'g' },
      { id: 'M55-calendar', en: 'Calendar', bn: 'ক্যালেন্ডার', t: 'g' }
    ]},
    { en: 'Scheduling', screens: [
      { id: 'M55-shifts', en: 'Shift Patterns', bn: 'শিফট', t: 'g' },
      { id: 'M55-rosters', en: 'Rosters & Publication', bn: 'রোস্টার', t: 'g' },
      { id: 'M55-publications', en: 'Roster Publication Approval', bn: 'রোস্টার প্রকাশ', t: 'g' },
      { id: 'M55-roster-changes', en: 'Roster Change Requests', bn: 'রোস্টার পরিবর্তন', t: 'g' },
      { id: 'M55-oncall', en: 'On-Call / Standby', bn: 'অন-কল', t: 'g' },
      { id: 'M55-availability', en: 'Availability → Dispatch', bn: 'প্রাপ্যতা', t: 'g' }
    ]}
  ],
  reports: ['Attendance Summary', 'Overtime Analysis', 'Leave Utilisation', 'Leave Balances', 'Roster vs Actual', 'Coverage Gaps'],
  forms: ['Leave Request', 'Roster', 'Shift Pattern', 'Exception Regularisation', 'Overtime Request', 'Night-Work Consent', 'Biometric Consent', 'Roster Publication', 'Roster Change Request', 'Working-Time Rule'],
  cross: ['M21 Workforce', 'M56 Payroll', 'M57 Incentives', 'M02 Dispatch'],
  freg: { src: 74, sub: [
    ['1', 'Capture (4 modes)', 12, { model: 'fix.attendance.record', cols: ['employee_id', 'check_in', 'check_out', 'source', 'approval_state'], screens: ['M55-daily', 'M55-devices', 'M55-geofence'] }],
    ['2', 'Working Time & OT', 9, { model: 'fix.attendance.record', cols: ['employee_id', 'week_start', 'worked_hours', 'overtime_hours', 'compliance_status'], screens: ['M55-rules'] }],
    ['3', 'Leave', 10, { model: 'fix.leave.request', cols: ['employee_id', 'leave_type_id', 'date_from', 'date_to', 'state'], screens: ['M55-leave', 'M55-balances', 'M55-calendar'] }],
    ['4', 'Holidays', 5, { model: 'fix.hr.holiday', cols: ['name', 'date', 'holiday_type', 'tentative'], screens: ['M55-holidays'] }],
    ['5', 'Shifts & Rosters', 13, { model: 'fix.roster.slot', cols: ['employee_id', 'date', 'shift_id', 'branch_id', 'on_leave'], screens: ['M55-shifts', 'M55-rosters'] }],
    ['6', 'On-Call', 6, { model: 'fix.hr.oncall', cols: ['name', 'employee_id', 'date_from', 'date_to', 'state'], screens: ['M55-oncall'] }],
    ['7', 'Availability Publication', 7, { model: 'fix.roster.slot', cols: ['date', 'branch_id', 'employee_id', 'shift_id'], screens: ['M55-availability', 'M55-rosters'], domain: [['on_leave', '=', false]] }],
    ['8', 'Verification & Lock', 6, { model: 'fix.attendance.lock', cols: ['name', 'period_start', 'period_end', 'state'], screens: ['M55-attendance-lock', 'M55-exc'] }],
    ['9', 'Timesheets', 6, { model: 'fix.attendance.record', cols: ['employee_id', 'check_in', 'check_out', 'worked_hours', 'overtime_hours'], screens: ['M55-daily'] }]
  ] }
};

export const SCREENS = {
  'M55-daily': { kind: 'model_list', model: 'fix.attendance.record', stateField: 'approval_state',
    cols: ['employee_id', 'check_in', 'check_out', 'source', 'worked_hours', 'recorded_overtime_hours', 'overtime_hours', 'approval_state'],
    actions: [
      { m: 'action_checkout', l: 'Clock Out' },
      { m: 'action_request_regularisation', l: 'Request Approval' }
    ] },
  'M55-devices': { kind: 'model_list', model: 'fix.biometric.device',
    cols: ['name', 'device_id', 'model_type', 'branch_id', 'ip_address', 'location_desc', 'status', 'active', 'last_sync_at', 'credential_prefix', 'credential_rotated_at'],
    note: 'Terminals post punches to /hooks/v1/biometric/<device id> with their own credential. Rotate Credential replaces it: give the new secret provisioned on the terminal (at least 32 characters). Only its hash is stored.',
    actions: [
      { m: 'action_rotate_credential', l: 'Rotate Credential', ask: 'New device credential (at least 32 characters)', kwarg: 'credential' }
    ] },
  'M55-hook-events': { kind: 'model_list', model: 'fix.biometric.punch.event', create: false, stateField: 'state',
    cols: ['device_id', 'event_ref', 'employee_id', 'punch_time', 'punch_type', 'state', 'record_id', 'message'] },
  'M55-bio-consent': { kind: 'model_list', model: 'fix.biometric.consent', stateField: 'state',
    cols: ['employee_id', 'notice_version', 'state', 'given_by_id', 'given_at', 'withdrawn_at'],
    note: 'No device punch is ingested for you without your consent to biometric processing (BRU-WFM-08). You give and withdraw it yourself; HR records it only against your signed consent. Mobile and manual entry remain open to you.',
    actions: [{ m: 'action_give', l: 'Give Consent' }, { m: 'action_withdraw', l: 'Withdraw Consent' }] },
  'M55-wt-rules': { kind: 'model_list', model: 'fix.working.time.rule',
    cols: ['name', 'company_id', 'version', 'date_from', 'date_to', 'weekly_limit_hours', 'min_rest_hours', 'rest_interval_after_hours', 'spread_over_max_hours', 'annual_avg_weekly_hours'],
    note: 'Valuation and the statutory checks read the version in force on the day. A version that has taken effect is never edited: record a new one from a future day. 0 means not checked.' },
  'M55-adjustments': { kind: 'model_list', model: 'fix.attendance.adjustment', create: false, stateField: 'state',
    cols: ['employee_id', 'date', 'period_month', 'kind', 'quantity', 'amount', 'state', 'approval_state', 'approved_by_id', 'payslip_ref_id'],
    note: 'A change to attendance in a month payroll has already paid is carried into the next payroll as an approved adjustment (FR-WFM-052). The person who made the change and the employee never approve it.',
    actions: [
      { m: 'action_inbox_approve', l: 'Approve' },
      { m: 'action_reject', l: 'Reject', ask: 'Reason for rejecting', kwarg: 'reason' }
    ] },
  'M55-geofence': { kind: 'model_list', model: 'fix.attendance.record',
    cols: ['employee_id', 'check_in', 'source', 'geo_lat', 'geo_long', 'accuracy_m', 'approval_state'] },
  'M55-exc': { kind: 'model_list', model: 'fix.attendance.record', stateField: 'approval_state',
    cols: ['employee_id', 'check_in', 'approval_reason', 'approval_state', 'approved_by'],
    domain: [['approval_state', '=', 'pending']],
    note: 'A pending record is decided by the employee\'s line manager, or an attendance officer when there is none. The requester, the creator and the employee never decide it. Approve and Reject decide your own routed task.',
    actions: [
      { m: 'action_request_regularisation', l: 'Request Approval' },
      { m: 'action_approve', l: 'Approve' },
      { m: 'action_reject', l: 'Reject', ask: 'Reason for rejecting', kwarg: 'reason' },
      { m: 'action_mark_rest_day', l: 'Mark Rest-Day Call-In' },
      { m: 'action_clear_rest_day', l: 'Clear Rest Day' }
    ] },
  'M55-regs': { kind: 'model_list', model: 'fix.attendance.regularisation', create: false, stateField: 'state',
    cols: ['name', 'employee_id', 'check_in_snapshot', 'check_out_snapshot', 'worked_hours_snapshot', 'reason', 'state', 'decided_by_id'],
    actions: [
      { m: 'action_inbox_approve', l: 'Approve' },
      { m: 'action_inbox_reject', l: 'Reject', ask: 'Reason for rejecting', kwarg: 'reason' }
    ] },
  'M55-ot': { kind: 'model_list', model: 'fix.overtime.request', stateField: 'state',
    cols: ['employee_id', 'date', 'hours', 'rest_day_work', 'retrospective', 'reason', 'state', 'approved_hours', 'decided_by_id'],
    actions: [
      { m: 'action_submit', l: 'Submit' },
      { m: 'action_inbox_approve', l: 'Approve' },
      { m: 'action_reject', l: 'Reject', ask: 'Reason for rejecting', kwarg: 'reason' },
      { m: 'action_cancel', l: 'Cancel' }
    ] },
  'M55-night': { kind: 'model_list', model: 'fix.night.work.consent', stateField: 'state',
    cols: ['employee_id', 'date_from', 'date_to', 'state', 'confirmed_by_id', 'confirmed_at'],
    actions: [{ m: 'action_confirm', l: 'Confirm Consent' }, { m: 'action_withdraw', l: 'Withdraw' }] },
  'M55-accrual': { kind: 'model_list', model: 'fix.leave.accrual', create: false,
    cols: ['employee_id', 'year_start', 'year_end', 'days_worked', 'days_earned', 'basis', 'computed_at'] },
  'M55-rules': { kind: 'table_report', module: 'M55', report: 'overtime_analysis', title: 'Rules & Overtime', period: true },
  'M55-holidays': { kind: 'model_list', model: 'fix.hr.holiday',
    cols: ['name', 'date', 'holiday_type', 'tentative', 'notes'] },
  'M55-leave': { kind: 'model_list', model: 'fix.leave.request', stateField: 'state',
    cols: ['employee_id', 'leave_type_id', 'date_from', 'date_to', 'days', 'reason', 'state', 'decided_by_id'],
    actions: [
      { m: 'action_submit', l: 'Submit' },
      { m: 'action_inbox_approve', l: 'Approve' },
      { m: 'action_reject', l: 'Reject', ask: 'Reason for rejecting', kwarg: 'reason' },
      { m: 'action_cancel', l: 'Cancel', ask: 'Reason for cancelling (required once approved)', kwarg: 'reason' }
    ] },
  'M55-balances': { kind: 'table_report', module: 'M55', report: 'leave_balances', title: 'Leave Balances', period: true },
  'M55-calendar': { kind: 'model_list', model: 'fix.leave.request', stateField: 'state',
    cols: ['employee_id', 'leave_type_id', 'date_from', 'date_to', 'days', 'state'] },
  'M55-shifts': { kind: 'model_list', model: 'fix.shift.template',
    cols: ['name', 'start_hour', 'end_hour', 'operating_unit_id'] },
  'M55-rosters': { kind: 'model_list', model: 'fix.roster.slot', stateField: 'state',
    cols: ['display_label', 'employee_id', 'date', 'shift_id', 'branch_id', 'state', 'on_leave', 'night_consent_flag'],
    note: 'Draft slots are the planner\'s; employees see a slot once its roster is published. A published slot changes only through a roster change request: ask for one on your own slot, and a supervisor completes and submits it.',
    actions: [
      { m: 'action_ask_change', l: 'Ask for a Change', ask: 'What needs to change, and why?', kwarg: 'reason' }
    ] },
  'M55-publications': { kind: 'model_list', model: 'fix.roster.publication', stateField: 'state',
    cols: ['name', 'date_from', 'date_to', 'branch_id', 'slot_count', 'state', 'planner_id', 'decided_by_id'],
    note: 'Submit collects the period\'s draft slots; another Attendance Supervisor (never the planner, never a rostered employee) approves and publishes them (BRU-WFM-12).',
    actions: [
      { m: 'action_submit', l: 'Submit for Publication' },
      { m: 'action_inbox_approve', l: 'Approve & Publish' },
      { m: 'action_reject', l: 'Reject', ask: 'Reason for rejecting', kwarg: 'reason' },
      { m: 'action_cancel', l: 'Recall' }
    ] },
  'M55-roster-changes': { kind: 'model_list', model: 'fix.roster.change.request', stateField: 'state',
    cols: ['name', 'kind', 'old_employee_id', 'old_date', 'old_shift_id', 'new_employee_id', 'new_date', 'new_shift_id', 'state', 'decided_by_id'],
    actions: [
      { m: 'action_submit', l: 'Submit' },
      { m: 'action_inbox_approve', l: 'Approve' },
      { m: 'action_reject', l: 'Reject', ask: 'Reason for rejecting', kwarg: 'reason' },
      { m: 'action_cancel', l: 'Cancel' }
    ] },
  'M55-oncall': { kind: 'model_list', model: 'fix.hr.oncall', stateField: 'state',
    cols: ['name', 'employee_id', 'shift_id', 'date_from', 'date_to', 'allowance', 'approval_state', 'approved_allowance', 'state'],
    actions: [
      { m: 'action_start', l: 'Start' },
      { m: 'action_complete', l: 'Complete' },
      { m: 'action_cancel', l: 'Cancel' },
      { m: 'action_submit_allowance', l: 'Request Allowance Approval' },
      { m: 'action_inbox_approve', l: 'Approve Allowance' },
      { m: 'action_reject_allowance', l: 'Reject Allowance', ask: 'Reason for rejecting', kwarg: 'reason' }
    ] },
  'M55-availability': { kind: 'table_report', module: 'M55', report: 'roster_vs_actual', title: 'Availability → Dispatch', period: true },

  /* Report chips -> their own computed pack */
  'M55-rpt-summary': { kind: 'table_report', module: 'M55', report: 'attendance_summary', title: 'Attendance Summary', period: true },
  'M55-rpt-ot': { kind: 'table_report', module: 'M55', report: 'overtime_analysis', title: 'Overtime Analysis', period: true },
  'M55-rpt-leave': { kind: 'table_report', module: 'M55', report: 'leave_utilisation', title: 'Leave Utilisation', period: true },
  'M55-rpt-balances': { kind: 'table_report', module: 'M55', report: 'leave_balances', title: 'Leave Balances', period: true },
  'M55-rpt-roster': { kind: 'table_report', module: 'M55', report: 'roster_vs_actual', title: 'Roster vs Actual', period: true },
  'M55-rpt-gaps': { kind: 'table_report', module: 'M55', report: 'coverage_gaps', title: 'Coverage Gaps', period: true },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M55-form-leave': {
    kind: 'model_form',
    model: 'fix.leave.request',
    title: 'Leave Request',
    back: 'M55-leave',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Submitted', approved: 'Approved', rejected: 'Rejected', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'details', label: 'Leave Particulars', bn: 'ছুটির বিবরণ', icon: '🗓️', badge: '6' },
      { id: 'evidence', label: 'Certificate & Confinement', bn: 'সনদ ও প্রসূতি', icon: '📎', badge: '3' },
      { id: 'approval', label: 'Reason & Decision', bn: 'কারণ ও অনুমোদন', icon: '🤝', badge: '7' }
    ],
    sections: [
      {
        tab: 'details',
        title: 'Statutory Leave Entitlement & Schedule',
        note: 'Bangladesh Labour Act 2006 statutory leave schedule (Casual s.115, Sick s.116, Annual s.117 at 1 day per 18 days worked after a year, Festival s.118). Days compute from the date range; confirmed public holidays are not charged (except maternity). Dates are fixed once submitted.',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'leave_type_id', required: true, label: 'Statutory Leave Type' },
          { name: 'date_from', required: true, label: 'From Date' },
          { name: 'date_to', required: true, label: 'To Date' },
          { name: 'days', label: 'Computed Days', readonly: true },
          { name: 'operating_unit_id', label: 'Branch / Operating Unit' }
        ]
      },
      {
        tab: 'evidence',
        title: 'Medical Certificate & Maternity',
        note: 'Sick leave is approved only with a registered medical practitioner\'s certificate (BLA s.116). Maternity needs the expected confinement date: 8 weeks before and 8 weeks after, after 6 months\' service (s.46-47).',
        fields: [
          { name: 'medical_certificate', label: 'Medical Certificate (Scanned File)', type: 'file' },
          { name: 'medical_certificate_name', label: 'Certificate File Name' },
          { name: 'expected_confinement_date', label: 'Expected Confinement Date (maternity)' }
        ]
      },
      {
        tab: 'approval',
        title: 'Justification & Decision',
        note: 'Submit routes the request to your line manager (HR when there is none). You never decide your own leave. An approved leave marks your roster days On-Leave, so dispatch does not assign you.',
        fields: [
          { name: 'reason', type: 'text', label: 'Reason for Absence' },
          { name: 'state', label: 'Status', readonly: true },
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'decided_by_id', label: 'Decided By', readonly: true },
          { name: 'decided_at', label: 'Decided At', readonly: true },
          { name: 'rejection_reason', label: 'Reason for Rejection', readonly: true },
          { name: 'cancel_reason', label: 'Reason for Cancellation', readonly: true },
          { name: 'coverage_flag', label: 'Team Coverage Below Threshold', readonly: true },
          { name: 'coverage_note', label: 'Team Coverage (BRU-WFM-04)', readonly: true }
        ]
      }
    ]
  },

  'M55-form-roster': {
    kind: 'model_form',
    model: 'fix.roster.slot',
    title: 'Roster Slot',
    back: 'M55-rosters',
    tabs: [
      { id: 'schedule', label: 'Roster Assignment', bn: 'রোস্টার শিডিউল', icon: '📅', badge: '3' },
      { id: 'location', label: 'Branch & Dispatch', bn: 'শাখা ও কর্মস্থল', icon: '📍', badge: '1' },
      { id: 'publication', label: 'Publication', bn: 'প্রকাশ', icon: '📣', badge: '5' }
    ],
    sections: [
      {
        tab: 'schedule',
        title: 'Shift Assignment Schedule',
        note: 'One technician, one date, one shift pattern. The primary availability answer consumed by M02 dispatch.',
        fields: [
          { name: 'employee_id', required: true, label: 'Technician / Employee' },
          { name: 'date', required: true, label: 'Roster Date' },
          { name: 'shift_id', required: true, label: 'Assigned Shift Pattern' }
        ]
      },
      {
        tab: 'location',
        title: 'Branch Location Scope',
        note: 'Operating branch or field service hub.',
        fields: [
          { name: 'branch_id', label: 'Operating Branch / Hub' }
        ]
      },
      {
        tab: 'publication',
        title: 'Publication & Change Control (BRU-WFM-12)',
        note: 'A draft slot is published with its roster once another supervisor approves it. After that its employee, day, shift and branch change only through a roster change request.',
        fields: [
          { name: 'state', label: 'Roster State', readonly: true },
          { name: 'publication_id', label: 'Roster Publication', readonly: true },
          { name: 'published_at', label: 'Published At', readonly: true },
          { name: 'on_leave', label: 'On Approved Leave', readonly: true },
          { name: 'night_consent_flag', label: 'Night-Work Consent Withdrawn (s.109)', readonly: true }
        ]
      }
    ]
  },

  'M55-form-shift': {
    kind: 'model_form',
    model: 'fix.shift.template',
    title: 'Shift Pattern',
    back: 'M55-shifts',
    tabs: [
      { id: 'timing', label: 'Schedule & Timing', bn: 'শিডিউল ও সময়', icon: '⏰', badge: '3' },
      { id: 'scope', label: 'Operating Unit', bn: 'শাখা ও ক্ষেত্র', icon: '📍', badge: '1' }
    ],
    sections: [
      {
        tab: 'timing',
        title: 'Shift Timing Definition',
        note: 'Start/end hours in decimal notation (e.g. 9.5 = 09:30). Must adhere to BLA s. 100/102 working hour regulations.',
        fields: [
          { name: 'name', required: true, label: 'Shift Name (e.g. Morning Tech Shift)' },
          { name: 'start_hour', required: true, label: 'Start Hour (decimal, e.g. 9.0)' },
          { name: 'end_hour', required: true, label: 'End Hour (decimal, e.g. 18.0)' }
        ]
      },
      {
        tab: 'scope',
        title: 'Operating Unit & Allocation',
        note: 'Branch operating unit scope.',
        fields: [
          { name: 'operating_unit_id', label: 'Operating Unit' }
        ]
      }
    ]
  },

  'M55-form-holiday': {
    kind: 'model_form',
    model: 'fix.hr.holiday',
    title: 'Holiday',
    back: 'M55-holidays',
    tabs: [
      { id: 'holiday', label: 'Holiday Particulars', bn: 'ছুটির বিবরণ', icon: '🌴', badge: '3' },
      { id: 'sighting', label: 'Moon Sighting Status', bn: 'চাঁদ দেখা সাপেক্ষে', icon: '🌙', badge: '1' }
    ],
    sections: [
      {
        tab: 'holiday',
        title: 'Statutory & Festival Holiday',
        note: 'Official public holidays under Bangladesh Labour Act 2006 s. 118 (Festival Holidays).',
        fields: [
          { name: 'name', required: true, label: 'Holiday Name (English)' },
          { name: 'name_bn', label: 'Holiday Name (Bengali)' },
          { name: 'date', required: true, label: 'Holiday Date' },
          { name: 'holiday_type', required: true, label: 'Holiday Category' }
        ]
      },
      {
        tab: 'sighting',
        title: 'Astronomical & Sighting Dependency',
        note: 'Eid/Shab-e-Barat/Shab-e-Qadr dates subject to National Moon Sighting Committee.',
        fields: [
          { name: 'tentative', label: 'Tentative (Subject to Moon Sighting)' }
        ]
      }
    ]
  },

  'M55-form-attendance-lock': {
    kind: 'model_form',
    model: 'fix.attendance.lock',
    title: "Attendance Lock",
    back: 'M55-attendance-lock',
    status: { field: 'state' },
    tabs: [
      { id: 'period', label: 'Lock Scope', bn: 'লক সময়সীমা', icon: '🔒', badge: '4' },
      { id: 'control', label: 'Workflow State', bn: 'অবস্থা', icon: '⚙️', badge: '8' }
    ],
    sections: [
      {
        tab: 'period',
        title: 'Monthly Attendance Cutoff Scope',
        note: 'Monthly cutoff lock for payroll calculation gating.',
        fields: [
          { name: 'name', required: true, label: 'Lock Reference' },
          { name: 'company_id', required: true, label: 'Company' },
          { name: 'period_start', required: true, label: 'Period Start Date' },
          { name: 'period_end', required: true, label: 'Period End Date' }
        ]
      },
      {
        tab: 'control',
        title: 'Operating Unit & Gating State',
        note: 'Lock Period locks a fully past period with no pending clock-ins; only then may payroll calculate. Re-opening needs the Attendance Lock Manager, a reason, and a payroll that has not yet taken the period.',
        fields: [
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'state', label: 'Lock State', readonly: true },
          { name: 'locked_by_id', label: 'Locked By', readonly: true },
          { name: 'locked_at', label: 'Locked At', readonly: true },
          { name: 'unlocked_by_id', label: 'Re-opened By', readonly: true },
          { name: 'unlock_reason', label: 'Reason for Re-opening', readonly: true },
          { name: 'unlock_count', label: 'Times Re-opened', readonly: true },
          { name: 'retro_flag', label: 'Re-locked After a Re-opening', readonly: true }
        ]
      }
    ]
  },

  /* ===== master-data forms (batch 2) — D365 in-workspace ===== */
  'M55-form-bio': {
    kind: 'model_form',
    model: 'fix.biometric.device',
    title: "Biometric Device",
    back: 'M55-devices',
    tabs: [
      { id: 'identity', label: 'Terminal Identity', bn: 'ডিভাইস পরিচয়', icon: '📟', badge: '4' },
      { id: 'network', label: 'Network & Branch', bn: 'নেটওয়ার্ক ও শাখা', icon: '🌐', badge: '3' },
      { id: 'sync', label: 'Status & Sync', bn: 'স্ট্যাটাস ও সিঙ্ক', icon: '🔄', badge: '2' }
    ],
    sections: [
      {
        tab: 'identity',
        title: "Biometric Attendance Terminal",
        note: "Hardware terminal serial and vendor model specification.",
        fields: [
          { name: 'company_id', required: true, label: "Company" },
          { name: 'device_id', required: true, label: "Device Serial / Identifier" },
          { name: 'name', required: true, label: "Terminal Name" },
          { name: 'model_type', required: true, label: "Terminal Hardware Model" }
        ]
      },
      {
        tab: 'network',
        title: "Branch Placement & IP Endpoint",
        note: "Network address and physical placement at branch or repair hub.",
        fields: [
          { name: 'branch_id', label: "Branch / Facility" },
          { name: 'ip_address', label: "IP Address / Hostname" },
          { name: 'location_desc', label: "Physical Location" }
        ]
      },
      {
        tab: 'sync',
        title: "Operational Status & Punch Sync",
        note: "Active terminal status and punch ingestion state.",
        fields: [
          { name: 'status', label: "Connection Status" },
          { name: 'active', label: "Active" },
          { name: 'last_sync_at', label: "Last Ingest Sync", readonly: true },
          { name: 'credential_prefix', label: "Webhook Credential Starts With", readonly: true },
          { name: 'credential_rotated_at', label: "Credential Rotated At", readonly: true },
          { name: 'credential_rotated_by_id', label: "Credential Rotated By", readonly: true }
        ]
      }
    ]
  },

  'M55-form-exception': {
    kind: 'model_form',
    model: 'fix.attendance.record',
    title: 'Attendance & Exception Record',
    back: 'M55-exc',
    status: { field: 'approval_state', labels: {
      pending: 'Pending', approved: 'Approved', rejected: 'Rejected' } },
    tabs: [
      { id: 'punch', label: 'Clock-In & Hours', bn: 'উপস্থিতি ও কর্মঘণ্টা', icon: '⏱️', badge: '9' },
      { id: 'geofence', label: 'Geofence & Regularisation', bn: 'জিওফেন্স ও অনুমোদন', icon: '📍', badge: '8' },
      { id: 'overtime', label: 'Weekly & Rest-Day OT (BLA s.108)', bn: 'সাপ্তাহিক অতিরিক্ত সময়', icon: '⚖️', badge: '6' }
    ],
    sections: [
      {
        tab: 'punch',
        title: 'Attendance Punch & Computed Hours',
        note: 'Biometric and mobile punches arrive from the devices and the technician app. What you type here is a MANUAL entry: give the reason; it is pending until your line manager (or an attendance officer) decides it. Changing the hours of a decided record sends it back for a decision.',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'check_in', required: true, label: 'Clock-In Timestamp' },
          { name: 'check_out', label: 'Clock-Out Timestamp' },
          { name: 'manual_reason', label: 'Reason for Manual Entry' },
          { name: 'source', label: 'Capture Source', readonly: true },
          { name: 'device_id', label: 'Registered Device', readonly: true },
          { name: 'worked_hours', label: 'Worked Hours', readonly: true },
          { name: 'recorded_overtime_hours', label: 'Recorded Overtime (beyond 8h a day)', readonly: true },
          { name: 'overtime_hours', label: 'Payable Overtime (approved, cap 2h a day)', readonly: true }
        ]
      },
      {
        tab: 'geofence',
        title: 'Geofence Coordinates & Exception Approval',
        note: 'GPS coordinates for field clock-ins and manager exception regularisation.',
        fields: [
          { name: 'geo_lat', label: 'GPS Latitude', readonly: true },
          { name: 'geo_long', label: 'GPS Longitude', readonly: true },
          { name: 'accuracy_m', label: 'GPS Accuracy (m)', readonly: true },
          { name: 'geofence_result', label: 'Geofence Result (server)', readonly: true },
          { name: 'approval_reason', label: 'Exception / Regularisation Reason', readonly: true },
          { name: 'approval_state', label: 'Approval State', readonly: true },
          { name: 'approved_by', label: 'Decided By', readonly: true },
          { name: 'approved_at', label: 'Decided At', readonly: true }
        ]
      },
      {
        tab: 'overtime',
        title: 'Statutory Weekly & Rest-Day Accumulator (BLA ss.100-108)',
        note: 'Weekly worked hours against the company weekly limit (a company setting; BLA s.102: 48h, 60h with overtime). The rest-day call-in is marked by the attendance supervisor, not by the employee.',
        fields: [
          { name: 'is_rest_day', label: 'Rest-Day Call-In (supervisor)', readonly: true },
          { name: 'rest_day_hours', label: 'Rest-Day Worked Hours', readonly: true },
          { name: 'holiday_hours', label: 'Public-Holiday Hours', readonly: true },
          { name: 'weekly_worked_hours', label: 'Cumulative Weekly Worked Hours', readonly: true },
          { name: 'weekly_ot_hours', label: 'Cumulative Weekly OT Hours', readonly: true },
          { name: 'weekly_ot_limit_exceeded', label: 'Weekly Limit Flag', readonly: true }
        ]
      }
    ]
  },

  'M55-form-oncall': {
    kind: 'model_form',
    model: 'fix.hr.oncall',
    title: 'On-Call / Standby Assignment',
    back: 'M55-oncall',
    status: { field: 'state', labels: {
      planned: 'Planned', active: 'Active', completed: 'Completed', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'schedule', label: 'Standby Schedule', bn: 'অন-কল সময়সূচি', icon: '📟', badge: '5' },
      { id: 'allowance', label: 'Allowance & Status', bn: 'ভাতা ও অবস্থা', icon: '💵', badge: '7' }
    ],
    sections: [
      {
        tab: 'schedule',
        title: 'Technician Standby Roster Window',
        note: 'After-hours emergency field support standby window.',
        fields: [
          { name: 'name', label: 'Standby Reference' },
          { name: 'employee_id', required: true, label: 'Technician / Employee' },
          { name: 'shift_id', label: 'Linked Shift Pattern' },
          { name: 'date_from', required: true, label: 'Standby Start' },
          { name: 'date_to', required: true, label: 'Standby End' }
        ]
      },
      {
        tab: 'allowance',
        title: 'Standby Allowance & Lifecycle',
        note: 'The allowance is approved by someone other than the person on call and the person who recorded it (line manager first). Payroll pays the approved figure; once approved it is not changed.',
        fields: [
          { name: 'allowance', label: 'Standby Allowance (BDT)' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'state', label: 'Standby State', readonly: true },
          { name: 'approval_state', label: 'Allowance Approval', readonly: true },
          { name: 'approved_allowance', label: 'Approved Allowance (paid)', readonly: true },
          { name: 'allowance_approved_by_id', label: 'Allowance Approved By', readonly: true },
          { name: 'allowance_approved_at', label: 'Allowance Approved At', readonly: true }
        ]
      }
    ]
  },

  'M55-form-ot': {
    kind: 'model_form',
    model: 'fix.overtime.request',
    title: 'Overtime Request',
    back: 'M55-ot',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Submitted', approved: 'Approved', rejected: 'Rejected', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'request', label: 'Overtime Requested', bn: 'অতিরিক্ত সময়', icon: '⏱️', badge: '6' },
      { id: 'decision', label: 'Decision', bn: 'সিদ্ধান্ত', icon: '✅', badge: '6' }
    ],
    sections: [
      {
        tab: 'request',
        title: 'Overtime Before It Is Worked (BRU-WFM-02)',
        note: 'Overtime is paid only where a request was approved: at most 2h a working day (BLA s.100/108), 10h on a weekly rest day. A request after the day is retrospective: it goes to HR and needs a full reason (BRU-WFM-03).',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'date', required: true, label: 'Overtime Date' },
          { name: 'hours', required: true, label: 'Hours Requested' },
          { name: 'rest_day_work', label: 'Weekly Rest-Day Work' },
          { name: 'reason', required: true, type: 'text', label: 'Reason' },
          { name: 'operating_unit_id', label: 'Operating Unit' }
        ]
      },
      {
        tab: 'decision',
        title: 'Routed Decision',
        note: 'Your line manager decides (HR for a retrospective request). You never decide your own overtime.',
        fields: [
          { name: 'state', label: 'Status', readonly: true },
          { name: 'retrospective', label: 'Retrospective', readonly: true },
          { name: 'approved_hours', label: 'Approved Hours', readonly: true },
          { name: 'decided_by_id', label: 'Decided By', readonly: true },
          { name: 'decided_at', label: 'Decided At', readonly: true },
          { name: 'rejection_reason', label: 'Reason for Rejection', readonly: true }
        ]
      }
    ]
  },

  'M55-form-night': {
    kind: 'model_form',
    model: 'fix.night.work.consent',
    title: 'Night-Work Consent (BLA s.109)',
    back: 'M55-night',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Given', withdrawn: 'Withdrawn' } },
    tabs: [
      { id: 'consent', label: 'Consent', bn: 'সম্মতি', icon: '🌙', badge: '5' },
      { id: 'record', label: 'Recorded', bn: 'নথিভুক্ত', icon: '🖊️', badge: '4' }
    ],
    sections: [
      {
        tab: 'consent',
        title: 'Work Between 10 p.m. and 6 a.m.',
        note: 'A woman is rostered between 10 p.m. and 6 a.m. only with her consent (BLA s.109). She confirms it herself, or HR records it against her signed consent; she may withdraw it at any time.',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'date_from', required: true, label: 'From' },
          { name: 'date_to', required: true, label: 'To' },
          { name: 'consent_file', label: 'Signed Consent (Scanned File)', type: 'file' },
          { name: 'consent_file_name', label: 'File Name' }
        ]
      },
      {
        tab: 'record',
        title: 'Who Recorded It',
        fields: [
          { name: 'state', label: 'Status', readonly: true },
          { name: 'confirmed_by_id', label: 'Recorded By', readonly: true },
          { name: 'confirmed_at', label: 'Recorded At', readonly: true },
          { name: 'withdrawn_at', label: 'Withdrawn At', readonly: true }
        ]
      }
    ]
  },

  'M55-form-bio-consent': {
    kind: 'model_form',
    model: 'fix.biometric.consent',
    title: 'Biometric Processing Consent (PDPA)',
    back: 'M55-bio-consent',
    status: { field: 'state', labels: { draft: 'Draft', given: 'Given', withdrawn: 'Withdrawn' } },
    tabs: [
      { id: 'consent', label: 'Consent', bn: 'সম্মতি', icon: '🖐️', badge: '4' },
      { id: 'record', label: 'Recorded', bn: 'নথিভুক্ত', icon: '🖊️', badge: '5' }
    ],
    sections: [
      {
        tab: 'consent',
        title: 'Specific Consent to Biometric Processing (BRU-WFM-08)',
        note: 'Biometric identifiers are sensitive personal data (PDPA 2026). HR prepares the consent record; you give it yourself (Give Consent), or HR records it from your signed consent; withdraw it at any time. Without it no device punch is ingested for you, and mobile or manual entry is used instead.',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'notice_version', label: 'Consent Notice Version' },
          { name: 'consent_file', label: 'Signed Consent (Scanned File)', type: 'file' },
          { name: 'consent_file_name', label: 'File Name' }
        ]
      },
      {
        tab: 'record',
        title: 'Who Recorded It',
        fields: [
          { name: 'state', label: 'Status', readonly: true },
          { name: 'given_by_id', label: 'Recorded By', readonly: true },
          { name: 'given_at', label: 'Given At', readonly: true },
          { name: 'withdrawn_by_id', label: 'Withdrawn By', readonly: true },
          { name: 'withdrawn_at', label: 'Withdrawn At', readonly: true }
        ]
      }
    ]
  },

  'M55-form-publication': {
    kind: 'model_form',
    model: 'fix.roster.publication',
    title: 'Roster Publication',
    back: 'M55-publications',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Awaiting Approval', published: 'Published', rejected: 'Rejected', cancelled: 'Recalled' } },
    tabs: [
      { id: 'period', label: 'Roster Period', bn: 'রোস্টার সময়কাল', icon: '📅', badge: '5' },
      { id: 'decision', label: 'Decision', bn: 'সিদ্ধান্ত', icon: '✅', badge: '8' }
    ],
    sections: [
      {
        tab: 'period',
        title: 'Draft Slots to Publish',
        note: 'Submit collects every draft slot of the company (and branch / operating unit, if set) in the period. A minimum notice applies when the company has set one (FR-WFM-041).',
        fields: [
          { name: 'company_id', required: true, label: 'Company' },
          { name: 'date_from', required: true, label: 'From' },
          { name: 'date_to', required: true, label: 'To' },
          { name: 'branch_id', label: 'Branch' },
          { name: 'operating_unit_id', label: 'Operating Unit' }
        ]
      },
      {
        tab: 'decision',
        title: 'Approved by Someone Other Than the Planner',
        fields: [
          { name: 'state', label: 'Status', readonly: true },
          { name: 'slot_count', label: 'Slots', readonly: true },
          { name: 'planner_id', label: 'Planned By', readonly: true },
          { name: 'submitted_at', label: 'Submitted At', readonly: true },
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'decided_by_id', label: 'Decided By', readonly: true },
          { name: 'decided_at', label: 'Decided At', readonly: true },
          { name: 'rejection_reason', label: 'Reason for Rejection', readonly: true }
        ]
      }
    ]
  },

  'M55-form-roster-change': {
    kind: 'model_form',
    model: 'fix.roster.change.request',
    title: 'Roster Change Request',
    back: 'M55-roster-changes',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Awaiting Approval', approved: 'Applied', rejected: 'Rejected', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'change', label: 'Change', bn: 'পরিবর্তন', icon: '🔁', badge: '7' },
      { id: 'decision', label: 'Decision', bn: 'সিদ্ধান্ত', icon: '✅', badge: '7' }
    ],
    sections: [
      {
        tab: 'change',
        title: 'Change to a Published Slot (BRU-WFM-12)',
        note: 'A supervisor raises it (or completes the one an employee asked for from the slot) and submits it; another supervisor approves. Leave a field empty to keep it.',
        fields: [
          { name: 'slot_id', required: true, label: 'Published Slot' },
          { name: 'kind', required: true, label: 'Change or Remove' },
          { name: 'new_employee_id', label: 'New Employee' },
          { name: 'new_date', label: 'New Date' },
          { name: 'new_shift_id', label: 'New Shift' },
          { name: 'new_branch_id', label: 'New Branch' },
          { name: 'reason', required: true, type: 'text', label: 'Reason' }
        ]
      },
      {
        tab: 'decision',
        title: 'What Was Rostered and Who Decided',
        fields: [
          { name: 'old_employee_id', label: 'Rostered Employee', readonly: true },
          { name: 'old_date', label: 'Rostered Date', readonly: true },
          { name: 'old_shift_id', label: 'Rostered Shift', readonly: true },
          { name: 'state', label: 'Status', readonly: true },
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'decided_by_id', label: 'Decided By', readonly: true },
          { name: 'rejection_reason', label: 'Reason for Rejection', readonly: true }
        ]
      }
    ]
  },

  'M55-form-wt-rule': {
    kind: 'model_form',
    model: 'fix.working.time.rule',
    title: 'Working-Time Rule Version',
    back: 'M55-wt-rules',
    tabs: [
      { id: 'version', label: 'Version', bn: 'সংস্করণ', icon: '🗂️', badge: '5' },
      { id: 'limits', label: 'Daily & Weekly Limits', bn: 'দৈনিক ও সাপ্তাহিক সীমা', icon: '⏱️', badge: '5' },
      { id: 'statutory', label: 'Statutory Checks', bn: 'বিধিবদ্ধ যাচাই', icon: '⚖️', badge: '9' }
    ],
    sections: [
      {
        tab: 'version',
        title: 'Effective-Dated Version (T-07)',
        note: 'A new version takes effect from a future day; one that has taken effect is never edited. Each attendance record stores the version it was valued with (T-08).',
        fields: [
          { name: 'company_id', required: true, label: 'Company' },
          { name: 'date_from', required: true, label: 'In Force From' },
          { name: 'version', label: 'Version', readonly: true },
          { name: 'date_to', label: 'In Force Until', readonly: true },
          { name: 'basis', type: 'text', label: 'Ruling / Basis' }
        ]
      },
      {
        tab: 'limits',
        title: 'BLA s.100, s.102, s.108 and the Company Rest Rule',
        fields: [
          { name: 'daily_max_hours', label: 'Daily Ceiling (h)' },
          { name: 'daily_ot_cap_hours', label: 'Daily Overtime Cap (h)' },
          { name: 'weekly_limit_hours', label: 'Weekly Limit (h)' },
          { name: 'min_rest_hours', label: 'Minimum Rest Between Shifts (h)' },
          { name: 'short_rest_mode', label: 'Short Rest: Label or Block' }
        ]
      },
      {
        tab: 'statutory',
        title: 'BLA s.101 Interval, s.105 Spread-Over, s.102 Annual Average',
        note: '0 means not checked. Label flags the attendance; Block refuses it.',
        fields: [
          { name: 'rest_interval_after_hours', label: 's.101 Interval Needed After (h)' },
          { name: 'rest_interval_minutes', label: 's.101 Interval Length (min)' },
          { name: 'rest_interval_after_hours_2', label: 's.101 Second Tier: After (h)' },
          { name: 'rest_interval_minutes_2', label: 's.101 Second Tier: Interval (min)' },
          { name: 'rest_interval_mode', label: 's.101: Label or Block' },
          { name: 'spread_over_max_hours', label: 's.105 Spread-Over Limit (h)' },
          { name: 'spread_over_mode', label: 's.105: Label or Block' },
          { name: 'annual_avg_weekly_hours', label: 's.102 Annual Average a Week (h)' },
          { name: 'annual_average_mode', label: 's.102 Average: Label or Block' }
        ]
      }
    ]
  },

  /* ===== triage coverage screens ===== */
  'M55-attendance-lock': { kind: 'model_list', model: 'fix.attendance.lock', stateField: 'state',
    cols: ['name', 'state', 'company_id', 'operating_unit_id', 'period_start', 'period_end'],
    actions: [
      { m: 'action_lock', l: 'Lock Period' },
      { m: 'action_unlock', l: 'Unlock Period', ask: 'Reason for re-opening the period', kwarg: 'reason' },
      { m: 'action_export_form10_overtime_register', l: 'Export Form 10 Overtime Register' }
    ] },

};

export const REPORT_ROUTES = {
  'M55:Attendance Summary': 'M55-rpt-summary',
  'M55:Overtime Analysis': 'M55-rpt-ot',
  'M55:Leave Utilisation': 'M55-rpt-leave',
  'M55:Leave Balances': 'M55-rpt-balances',
  'M55:Roster vs Actual': 'M55-rpt-roster',
  'M55:Coverage Gaps': 'M55-rpt-gaps'
};

export const FORM_MODELS = {
  'M55:Leave Request': 'fix.leave.request',
  'M55:Roster': 'fix.roster.slot',
  'M55:Shift Pattern': 'fix.shift.template',
  'M55:Exception Regularisation': 'fix.attendance.record',
  'M55:Overtime Request': 'fix.overtime.request',
  'M55:Night-Work Consent': 'fix.night.work.consent',
  'M55:Biometric Consent': 'fix.biometric.consent',
  'M55:Roster Publication': 'fix.roster.publication',
  'M55:Roster Change Request': 'fix.roster.change.request',
  'M55:Working-Time Rule': 'fix.working.time.rule'
};

export const FORM_CHIPS = {
  'M55:Biometric Device': 'M55-form-bio',
  'M55:Leave Request': 'M55-form-leave',
  'M55:Roster': 'M55-form-roster',
  'M55:Shift Pattern': 'M55-form-shift',
  'M55:Exception Regularisation': 'M55-form-exception',
  'M55:Overtime Request': 'M55-form-ot',
  'M55:Night-Work Consent': 'M55-form-night',
  'M55:Biometric Consent': 'M55-form-bio-consent',
  'M55:Roster Publication': 'M55-form-publication',
  'M55:Roster Change Request': 'M55-form-roster-change',
  'M55:Working-Time Rule': 'M55-form-wt-rule',
  'M55:__by_model__': {
    'fix.attendance.lock': 'M55-form-attendance-lock',
    'fix.biometric.device': 'M55-form-bio',
    'fix.leave.request': 'M55-form-leave',
    'fix.roster.slot': 'M55-form-roster',
    'fix.shift.template': 'M55-form-shift',
    'fix.attendance.record': 'M55-form-exception',
    'fix.hr.holiday': 'M55-form-holiday',
    'fix.hr.oncall': 'M55-form-oncall',
    'fix.overtime.request': 'M55-form-ot',
    'fix.night.work.consent': 'M55-form-night',
    'fix.biometric.consent': 'M55-form-bio-consent',
    'fix.roster.publication': 'M55-form-publication',
    'fix.roster.change.request': 'M55-form-roster-change',
    'fix.working.time.rule': 'M55-form-wt-rule'
  },
  'M55:__by_screen__': {
    'M55-attendance-lock': 'M55-form-attendance-lock',
    'M55-daily': 'M55-form-exception',
    'M55-devices': 'M55-form-bio',
    'M55-leave': 'M55-form-leave',
    'M55-calendar': 'M55-form-leave',
    'M55-rosters': 'M55-form-roster',
    'M55-shifts': 'M55-form-shift',
    'M55-geofence': 'M55-form-exception',
    'M55-exc': 'M55-form-exception',
    'M55-holidays': 'M55-form-holiday',
    'M55-oncall': 'M55-form-oncall',
    'M55-ot': 'M55-form-ot',
    'M55-night': 'M55-form-night',
    'M55-bio-consent': 'M55-form-bio-consent',
    'M55-publications': 'M55-form-publication',
    'M55-roster-changes': 'M55-form-roster-change',
    'M55-wt-rules': 'M55-form-wt-rule'
  }
};

export const CREATE = {
  M55: { screen: 'M55-form-leave', model: 'fix.leave.request', label: 'Leave Request' }
};
