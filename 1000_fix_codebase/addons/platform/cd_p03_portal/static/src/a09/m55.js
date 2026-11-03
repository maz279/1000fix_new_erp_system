/** @odoo-module **/
/* A09 · People & Workforce — M55 Time, Attendance & Scheduling.
 * Registry-faithful: 4 groups / 13 screens / 5 reports / 4 forms / freg 74. */

export const MODULE = {
  area: 'A09', code: 'M55', en: 'Time, Attendance & Scheduling', title: 'M55 · Time, Attendance & Scheduling',
  bn: 'সময়, উপস্থিতি ও শিডিউলিং', icon: '⏰',
  desc: 'Biometric and geofenced capture, exception regularisation, working-time rules and overtime, moon-dependent holidays, leave requests and balances, shift patterns, rosters and publication, on-call standby, and availability published to dispatch.',
  kpis: [
    { l: 'Attendance Today', m: 'attendance_today' },
    { l: 'Exceptions Pending', m: 'exceptions_pending' },
    { l: 'Overtime Approved', m: 'overtime_preapproved' },
    { l: 'Roster Coverage', m: 'roster_coverage', suffix: '%' },
    { l: 'Leave Pending', m: 'leave_pending' },
    { l: 'Geofence Clock-Ins', m: 'geofence_clockins' }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M55-attendance-lock', en: "Attendance Lock", bn: "উপস্থিতি লক", t: 'g' }
    ]},
    { en: 'Capture', screens: [
      { id: 'M55-daily', en: 'Daily Attendance', bn: 'দৈনিক উপস্থিতি', t: 'g' },
      { id: 'M55-devices', en: 'Biometric Devices', bn: 'বায়োমেট্রিক', t: 'g' },
      { id: 'M55-geofence', en: 'Geofenced Clock-In', bn: 'জিওফেন্স', t: 'g' },
      { id: 'M55-exc', en: 'Exception Regularisation', bn: 'ব্যতিক্রম নিয়মিতকরণ', t: 'g' }
    ]},
    { en: 'Working Time', screens: [
      { id: 'M55-rules', en: 'Rules & Overtime', bn: 'নিয়ম ও অতিরিক্ত সময়', t: 'r' },
      { id: 'M55-holidays', en: 'Holidays (moon-dependent)', bn: 'ছুটির দিনপঞ্জি', t: 'g' }
    ]},
    { en: 'Leave', screens: [
      { id: 'M55-leave', en: 'Leave Requests', bn: 'ছুটির আবেদন', t: 'g' },
      { id: 'M55-balances', en: 'Balances', bn: 'ব্যালান্স', t: 'r' },
      { id: 'M55-calendar', en: 'Calendar', bn: 'ক্যালেন্ডার', t: 'g' }
    ]},
    { en: 'Scheduling', screens: [
      { id: 'M55-shifts', en: 'Shift Patterns', bn: 'শিফট', t: 'g' },
      { id: 'M55-rosters', en: 'Rosters & Publication', bn: 'রোস্টার', t: 'g' },
      { id: 'M55-oncall', en: 'On-Call / Standby', bn: 'অন-কল', t: 'g' },
      { id: 'M55-availability', en: 'Availability → Dispatch', bn: 'প্রাপ্যতা', t: 'g' }
    ]}
  ],
  reports: ['Attendance Summary', 'Overtime Analysis', 'Leave Utilisation', 'Roster vs Actual', 'Coverage Gaps'],
  forms: ['Leave Request', 'Roster', 'Shift Pattern', 'Exception Regularisation'],
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
    cols: ['employee_id', 'check_in', 'check_out', 'source', 'worked_hours', 'overtime_hours', 'approval_state'],
    actions: [{ m: 'action_checkout', l: 'Clock Out' }] },
  'M55-devices': { kind: 'model_list', model: 'fix.biometric.device',
    cols: ['name', 'device_id', 'model_type', 'branch_id', 'ip_address', 'location_desc', 'status', 'active'],
    actions: [{ m: 'action_ingest_punch', l: 'Ingest Punches' }] },
  'M55-geofence': { kind: 'model_list', model: 'fix.attendance.record',
    cols: ['employee_id', 'check_in', 'source', 'geo_lat', 'geo_long', 'accuracy_m', 'approval_state'] },
  'M55-exc': { kind: 'model_list', model: 'fix.attendance.record', stateField: 'approval_state',
    cols: ['employee_id', 'check_in', 'approval_reason', 'approval_state', 'approved_by'],
    actions: [{ m: 'action_approve', l: 'Approve' }, { m: 'action_reject', l: 'Reject' }] },
  'M55-rules': { kind: 'table_report', module: 'M55', report: 'overtime_analysis', title: 'Rules & Overtime', period: true },
  'M55-holidays': { kind: 'model_list', model: 'fix.hr.holiday',
    cols: ['name', 'date', 'holiday_type', 'tentative', 'notes'] },
  'M55-leave': { kind: 'model_list', model: 'fix.leave.request', stateField: 'state',
    cols: ['employee_id', 'leave_type_id', 'date_from', 'date_to', 'days', 'reason', 'state'],
    actions: [{ m: 'action_approve', l: 'Approve' }] },
  'M55-balances': { kind: 'table_report', module: 'M55', report: 'leave_utilisation', title: 'Leave Utilisation', period: true },
  'M55-calendar': { kind: 'model_list', model: 'fix.leave.request', stateField: 'state',
    cols: ['employee_id', 'leave_type_id', 'date_from', 'date_to', 'days', 'state'] },
  'M55-shifts': { kind: 'model_list', model: 'fix.shift.template',
    cols: ['name', 'start_hour', 'end_hour', 'operating_unit_id'] },
  'M55-rosters': { kind: 'model_list', model: 'fix.roster.slot',
    cols: ['display_label', 'employee_id', 'date', 'shift_id', 'branch_id', 'on_leave'] },
  'M55-oncall': { kind: 'model_list', model: 'fix.hr.oncall', stateField: 'state',
    cols: ['name', 'employee_id', 'shift_id', 'date_from', 'date_to', 'allowance', 'state'],
    actions: [
      { m: 'action_start', l: 'Start' },
      { m: 'action_complete', l: 'Complete' },
      { m: 'action_cancel', l: 'Cancel' }
    ] },
  'M55-availability': { kind: 'table_report', module: 'M55', report: 'roster_vs_actual', title: 'Availability → Dispatch', period: true },

  /* Report chips -> their own computed pack */
  'M55-rpt-summary': { kind: 'table_report', module: 'M55', report: 'attendance_summary', title: 'Attendance Summary', period: true },
  'M55-rpt-ot': { kind: 'table_report', module: 'M55', report: 'overtime_analysis', title: 'Overtime Analysis', period: true },
  'M55-rpt-leave': { kind: 'table_report', module: 'M55', report: 'leave_utilisation', title: 'Leave Utilisation', period: true },
  'M55-rpt-roster': { kind: 'table_report', module: 'M55', report: 'roster_vs_actual', title: 'Roster vs Actual', period: true },
  'M55-rpt-gaps': { kind: 'table_report', module: 'M55', report: 'coverage_gaps', title: 'Coverage Gaps', period: true },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M55-form-leave': {
    kind: 'model_form',
    model: 'fix.leave.request',
    title: 'Leave Request',
    back: 'M55-leave',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Submitted', approved: 'Approved', rejected: 'Rejected' } },
    tabs: [
      { id: 'details', label: 'Leave Particulars', bn: 'ছুটির বিবরণ', icon: '🗓️', badge: '6' },
      { id: 'approval', label: 'Reason & Handover', bn: 'কারণ ও অনুমোদন', icon: '🤝', badge: '2' }
    ],
    sections: [
      {
        tab: 'details',
        title: 'Statutory Leave Entitlement & Schedule',
        note: 'Bangladesh Labour Act 2006 statutory leave schedule (Casual s.115, Sick s.116, Annual s.117, Festival s.118). Days compute automatically from date range.',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'leave_type_id', required: true, label: 'Statutory Leave Type' },
          { name: 'date_from', required: true, label: 'From Date' },
          { name: 'date_to', required: true, label: 'To Date' },
          { name: 'days', label: 'Computed Days' },
          { name: 'operating_unit_id', label: 'Branch / Operating Unit' }
        ]
      },
      {
        tab: 'approval',
        title: 'Operational Justification & Workflow',
        note: 'Approved requests automatically mark technician availability as On-Leave in M02 Dispatch.',
        fields: [
          { name: 'reason', type: 'text', label: 'Reason for Absence' },
          { name: 'state', required: true, label: 'Approval State' }
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
      { id: 'location', label: 'Branch & Dispatch', bn: 'শাখা ও কর্মস্থল', icon: '📍', badge: '1' }
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
      { id: 'control', label: 'Workflow State', bn: 'অবস্থা', icon: '⚙️', badge: '2' }
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
        note: 'Approved lock permits payroll calculator execution.',
        fields: [
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'state', required: true, label: 'Lock State' }
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
          { name: 'active', label: "Active" }
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
      { id: 'punch', label: 'Clock-In & Hours', bn: 'উপস্থিতি ও কর্মঘণ্টা', icon: '⏱️', badge: '6' },
      { id: 'geofence', label: 'Geofence & Regularisation', bn: 'জিওফেন্স ও অনুমোদন', icon: '📍', badge: '6' },
      { id: 'overtime', label: 'Weekly & Rest-Day OT (BLA s.108)', bn: 'সাপ্তাহিক অতিরিক্ত সময়', icon: '⚖️', badge: '5' }
    ],
    sections: [
      {
        tab: 'punch',
        title: 'Attendance Punch & Computed Hours',
        note: 'Biometric or mobile clock-in/out timestamps and statutory daily hours.',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'check_in', required: true, label: 'Clock-In Timestamp' },
          { name: 'check_out', label: 'Clock-Out Timestamp' },
          { name: 'source', required: true, label: 'Capture Source' },
          { name: 'worked_hours', label: 'Worked Hours' },
          { name: 'overtime_hours', label: 'Daily Overtime Hours (Cap 2h s.100)' }
        ]
      },
      {
        tab: 'geofence',
        title: 'Geofence Coordinates & Exception Approval',
        note: 'GPS coordinates for field clock-ins and manager exception regularisation.',
        fields: [
          { name: 'geo_lat', label: 'GPS Latitude' },
          { name: 'geo_long', label: 'GPS Longitude' },
          { name: 'accuracy_m', label: 'GPS Accuracy (m)' },
          { name: 'approval_reason', label: 'Exception / Regularisation Reason' },
          { name: 'approved_by', label: 'Approved By Manager' },
          { name: 'approval_state', required: true, label: 'Approval State' }
        ]
      },
      {
        tab: 'overtime',
        title: 'Statutory Weekly & Rest-Day Accumulator (BLA ss.100-108)',
        note: 'Tracks weekly worked hours (max 60h), weekly overtime (max 12h), and Friday/Saturday rest-day hours.',
        fields: [
          { name: 'is_rest_day', label: 'Rest Day / Holiday Work' },
          { name: 'rest_day_hours', label: 'Rest-Day Worked Hours' },
          { name: 'weekly_worked_hours', label: 'Cumulative Weekly Worked Hours' },
          { name: 'weekly_ot_hours', label: 'Cumulative Weekly OT Hours' },
          { name: 'weekly_ot_limit_exceeded', label: 'Weekly Statutory Limit Flag' }
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
      scheduled: 'Scheduled', active: 'Active', completed: 'Completed', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'schedule', label: 'Standby Schedule', bn: 'অন-কল সময়সূচি', icon: '📟', badge: '5' },
      { id: 'allowance', label: 'Allowance & Status', bn: 'ভাতা ও অবস্থা', icon: '💵', badge: '3' }
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
        note: 'Fixed on-call standby allowance and completion status.',
        fields: [
          { name: 'allowance', label: 'Standby Allowance (BDT)' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'state', required: true, label: 'Standby State' }
        ]
      }
    ]
  },

  /* ===== triage coverage screens ===== */
  'M55-attendance-lock': { kind: 'model_list', model: 'fix.attendance.lock', stateField: 'state',
    cols: ['name', 'state', 'company_id', 'operating_unit_id', 'period_start', 'period_end'],
    actions: [
      { m: 'action_lock', l: 'Lock Period' },
      { m: 'action_unlock', l: 'Unlock Period' },
      { m: 'action_export_form10_overtime_register', l: 'Export Form 10 Overtime Register' }
    ] },

};

export const REPORT_ROUTES = {
  'M55:Attendance Summary': 'M55-rpt-summary',
  'M55:Overtime Analysis': 'M55-rpt-ot',
  'M55:Leave Utilisation': 'M55-rpt-leave',
  'M55:Roster vs Actual': 'M55-rpt-roster',
  'M55:Coverage Gaps': 'M55-rpt-gaps'
};

export const FORM_MODELS = {
  'M55:Leave Request': 'fix.leave.request',
  'M55:Roster': 'fix.roster.slot',
  'M55:Shift Pattern': 'fix.shift.template',
  'M55:Exception Regularisation': 'fix.attendance.record'
};

export const FORM_CHIPS = {
  'M55:Biometric Device': 'M55-form-bio',
  'M55:Leave Request': 'M55-form-leave',
  'M55:Roster': 'M55-form-roster',
  'M55:Shift Pattern': 'M55-form-shift',
  'M55:Exception Regularisation': 'M55-form-exception',
  'M55:__by_model__': {
    'fix.attendance.lock': 'M55-form-attendance-lock',
    'fix.biometric.device': 'M55-form-bio',
    'fix.leave.request': 'M55-form-leave',
    'fix.roster.slot': 'M55-form-roster',
    'fix.shift.template': 'M55-form-shift',
    'fix.attendance.record': 'M55-form-exception',
    'fix.hr.holiday': 'M55-form-holiday',
    'fix.hr.oncall': 'M55-form-oncall'
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
    'M55-oncall': 'M55-form-oncall'
  }
};

export const CREATE = {
  M55: { screen: 'M55-form-leave', model: 'fix.leave.request', label: 'Leave Request' }
};
