# cd_attendance — M55 Time, Attendance & Scheduling (P08-M02).
{
    "name": "1000FiX Time & Attendance",
    "summary": "M55: attendance records, shifts/rosters, working-time compliance, the attendance lock payroll depends on (CD-M55-nn)",
    "description": """
CD-M55-01 (P08-M02) — Wave 5 attendance:

- fix.attendance.record — check-in/out with source (biometric INT-041,
  mobile geofenced P02 flow, manual); worked-hours compute; records are
  IMMUTABLE once their period is locked
- fix.shift.template / fix.roster.slot — shift and roster management;
  the roster CLOSES the M02 -> M55 availability stub (P05-M03-T05): the
  W2 seam returned "available within working calendar"; dispatch now asks
  the ROSTER
- fix.attendance.lock — the monthly lock that payroll depends on
  (P08-M02-T05): journey 13 runs attendance lock -> calculation ->
  approval -> BEFTN -> payslips -> posting
- working-time compliance (SC-008): daily 8h standard, OT hours flagged
  beyond it, weekly rest-day verification
- biometric templates are S3 residency data: only the device reference
  lands here; the template itself routes through fix.identity.document
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Human Resources/Attendance",
    "depends": [
        "base",
        "mail",
        "hr",
        "hr_attendance",
        "cd_entity_config",
        "cd_hr_core",
        "cd_employee_core",
        "cd_event_outbox",
        "cd_service_order",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/fix_a09_groups.xml",
        "security/ir.model.access.csv",
        # A09 P0-b/P1/P2 (M55): own-record rules and the routing cron
        "security/fix_a09_attendance_rules.xml",
        "data/fix_a09_attendance_data.xml",
        "data/wfm_sequences.xml",
        "views/fix_attendance_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M55-01",
    "x_module_id": "M55",
    "x_wave": "W5",
    "x_owner": "People",
    "x_category": "H_People_Payroll_and_Quality",
    "x_tier": "T8",
}
