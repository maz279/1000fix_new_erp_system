# cd_competency — M22 Learning, Competency & Certification (P08-M05).
{
    "name": "1000FiX Competency & Certification",
    "summary": "M22: competency register, certification expiry tracking, FR-LMS-039 dispatch eligibility — closes the M02/M31 -> M22 stubs (CD-M22-nn)",
    "description": """
CD-M22-01 (P08-M05) — the LMS re-scoped (technical content authoring
degrades to M61, accepted AR-006 5.4):

- fix.competency — the competency register with device-type/brand scope
- fix.certification — employee certifications with EXPIRY tracking and
  the status compute (active/expiring/expired); emits
  certification.granted / certification.expired (P08-M05-T09)
- fix.training.course / fix.training.enrollment — course packs (the 24
  TR-* content files and 08B packs are loaded content pointers)
- FR-LMS-039 — dispatch_eligibility(): the real eligibility check.
  Closes the M02 -> M22 stub (P05-M03-T05) and the M31 -> M22 stub
  (P05-M02-T05): an UNCERTIFIED technician must NOT be assignable —
  a blocking error retrofitted into the live assignment path, exactly
  why the seam was built in W2
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Human Resources/Learning",
    "depends": ["base", "mail", "cd_entity_config", "cd_hr_core",
                 "cd_event_outbox", "cd_service_order"],
    "data": ["security/ir.model.access.csv", "views/fix_competency_views.xml"],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M22-01",
    "x_module_id": "M22",
    "x_wave": "W5",
    "x_owner": "People",
    "x_category": "H_People_Payroll_and_Quality",
    "x_tier": "T8",
}
