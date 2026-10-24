# cd_payroll_bd — M56 Payroll & Statutory Compliance (P08-M03). P0 module.
{
    "name": "1000FiX Payroll BD",
    "summary": "M56: payroll engine (FY2026-27 slabs), PF/gratuity Act-2026, BEFTN batch calendar, Bengali payslips, GL posting (CD-M56-nn)",
    "description": """
CD-M56-01 (P08-M03) — the only P0 module in Category H:

- fix.payroll.period — journey 13's spine: draft -> attendance_locked ->
  calculated -> approved -> paid -> posted. Calculation is REFUSED until
  the month's attendance lock is locked (P08-M02-T05)
- fix.payslip — every line computed by libs/py/payroll_engine (the ONLY
  calculation authority, DoD-03 100% covered): FY 2026-27 income-tax
  slabs (375k threshold; 10/15/20/25/30), provident fund wings,
  2x overtime; gratuity + resignation compensation per the Labour
  (Amendment) Act 2026 on separation
- fix.beftn.batch — INT-005 with the batch model: settlement date from
  the engine's cut-off calendar (16:00, Fri/Sat/holiday -> next working
  day, Sunday-Thursday week). A run that misses the cut-off pays late —
  modelled, not hoped away
- payslip.pdf — the Bengali payslip (TR-07's named failure mode)
- GL posting to M19 on approval; approval SoD negative-tested
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Human Resources/Payroll",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_hr_core",
        "cd_attendance",
        "cd_gl_ext",
        "cd_event_outbox",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/fix_payroll_security.xml",
        "security/ir.model.access.csv",
        "views/fix_payroll_views.xml",
    ],
    "installable": True,
    "application": True,
    "x_cd_id": "CD-M56-01",
    "x_module_id": "M56",
    "x_wave": "W5",
    "x_owner": "People",
    "x_category": "H_People_Payroll_and_Quality",
    "x_tier": "T8",
}
