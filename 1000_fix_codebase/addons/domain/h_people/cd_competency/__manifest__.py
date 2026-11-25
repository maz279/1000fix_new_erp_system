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
- A09 remediation: certification grant routed to a verifier (assessment,
  expiry and evidence required, no duplicates, no self-certification);
  frozen once granted; renew / suspend / reinstate / revoke; daily expiry
  cron; the waiver is an approved, reasoned fix.certification.waiver;
  assessments follow the pass mark; OJT signed off by the mentor; ISO
  evidence submitted and accepted by different users with a file
- A09 round 2: consumers of certification.expired/.suspended/.revoked
  (dispatcher to-dos on not-started jobs; starting work re-checks
  eligibility) and training.passed (competence evidence); the statutory /
  safety certification class escalated to M59 on lapse; the yearly training
  budget with routed over-budget approval; the attempt-limit escalation;
  the repair tier on work orders
- M22 capture pass 2: role competency requirements and the gap analysis,
  training needs and plans, participant feedback, enrolment withdrawal and
  substitution, mentoring with its interactions, effectiveness evaluation
- A09 R2 audit fixes: an un-tiered certification no longer satisfies a
  tiered job (M22-F3); the workshop fail-closed switch
  (cd_competency.workshop_gate_fail_closed, M22-F2); the work-order gate
  refuses before the assignment is written (M22-F12);
  training.session.scheduled flags the trainees' roster slots (M22-F4,
  FR-LMS-022) and the 90-day effectiveness + monthly coverage/SPOF crons run
  (AUT-LMS-12/13); the brand_critical flag and dual employee+manager expiry
  alerts (M22-F8); superuser overrides are logged on the mail thread
  (M22-F11); business dates are Asia/Dhaka (M22-F13); the catalogue
  skill-profile gate covers service operations (M22-F10)
""",
    "version": "19.0.0.5.1",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Human Resources/Learning",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_hr_core",
        "cd_event_outbox",
        "cd_service_order",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/fix_a09_groups.xml",
        "security/ir.model.access.csv",
        "security/fix_a09_privacy_rules.xml",
        "security/fix_a09_m22_capture2_rules.xml",
        "data/competency_ops_sequences.xml",
        "data/fix_a09_competency_data.xml",
        "data/fix_a09_m22_r2_data.xml",
        "views/fix_competency_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M22-01",
    "x_module_id": "M22",
    "x_wave": "W5",
    "x_owner": "People",
    "x_category": "H_People_Payroll_and_Quality",
    "x_tier": "T8",
}
