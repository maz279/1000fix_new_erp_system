# cd_hr_core — M21 Core HR complete (P08-M01).
{
    "name": "1000FiX Core HR",
    "summary": "M21 full: employment contracts (Labour Act artefacts), statutory leave, org structure (CD-M21-nn)",
    "description": """
CD-M21-01 (P08-M01) — the W5 completion of the employee estate on the W1
master slice (cd_employee_core):

- fix.employment.contract — Labour Act 2006 employment artefacts: contract
  types, probation capped at 6 months (s.4 Rules), statutory weekly hours,
  basic salary (Monetary, AS-10); lifecycle with renewal escalation
- fix.leave.type / fix.leave.request — statutory entitlements per the
  Bangladesh Labour Act 2006 (annual 20, sick 14, maternity 16 weeks,
  festival 11) with earned-rate validation and encashment flag
- fix.org.position — reporting lines and position management
- hr.employee extension — employee code + residency routing: the NID, birth
  registration and e-TIN go to the Bangladesh-resident store (Z4) through
  libs/py/fix_residency; hr_employee keeps a pointer and a keyed hash, and
  every read is logged (A09 M21-A6, BRU-HCM-06/07)
- joiner/mover/leaver events (AS-08) verified to drive M29 provisioning at
  full scale (P08-M01-T06)
""",
    "version": "19.0.0.6.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Human Resources",
    "depends": [
        "base",
        "mail",
        "hr",
        "hr_holidays",
        "cd_entity_config",
        "cd_employee_core",
        "cd_event_outbox",
        "cd_party_master",
        "cd_document_core",
        # M63 approval engine: every A09 approval is a routed request
        "cd_workflow_engine",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/fix_a09_groups.xml",
        # M21 decision roles (A09 P0-b): legal, executive, finance, clearance owners
        "security/fix_a09_m21_groups.xml",
        "security/ir.model.access.csv",
        "security/fix_a09_privacy_rules.xml",
        # A09 round 2: the identity read log and the s.27(3A) case
        "security/fix_a09_m21_r2_rules.xml",
        # M21 capture audit: notice acknowledgement and exit interview
        "security/fix_a09_m21_capture_rules.xml",
        # M21 capture audit pass 2: probation review, knowledge handover,
        # additional assignment
        "security/fix_a09_m21_capture2_rules.xml",
        # M55 leave controls (A09 P0-b/P1/P2); owned by the leave work package
        "security/leave/ir.model.access.csv",
        "data/fix_a09_leave_data.xml",
        "data/statutory_leave_data.xml",
        "data/hr_ops_sequences.xml",
        "data/employment_contract_templates.xml",
        "data/identity_lifecycle_cron.xml",
        # M21 crons and the employee.left relay consumer (A09 C3/C5)
        "data/fix_a09_m21_data.xml",
        "views/fix_hr_core_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M21-01",
    "x_module_id": "M21",
    "x_wave": "W5",
    "x_owner": "People",
    "x_category": "H_People_Payroll_and_Quality",
    "x_tier": "T8",
}
