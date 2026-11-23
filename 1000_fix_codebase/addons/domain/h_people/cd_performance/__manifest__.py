# cd_performance — M57 Performance, Incentives & Compensation (P08-M04).
{
    "name": "1000FiX Performance & Incentives",
    "summary": "M57: technician scorecard, incentive engine (feeds payroll), compensation bands (T5-protected) (CD-M57-nn)",
    "description": """
CD-M57-01 (P08-M04):

- fix.performance.scorecard — the technician scorecard surfaced in P02
  (the app exposes it; the model lands here): first-time-fix, CSAT,
  SLA-hit, rework rate -> composite score, computed from service orders
- fix.incentive.run / fix.incentive.line — the incentive calculation
  engine: banded score -> amount (Monetary, AS-10); it FEEDS payroll
  (the payslip's incentive field); 100% covered (DoD-03 — it pays people)
- fix.compensation.band — bands and ranges; compensation data is T5-tier:
  the amounts are field-protected (Compensation Manager) and
  negative-testable (DoD-07); contracts are checked against them (I7)
- A09 remediation: own roles; incentive runs draft -> computed -> approved
  through the routed approval engine, lines frozen, one run per period;
  payroll picks approved lines up (I4) — M57 never writes the payslip;
  review cycle with self-assessment, line-manager rating and routed
  calibration; agreed goals; guarded PIPs; recognition prizes approved
- A09 round 2: incentive schemes with effective-dated versions approved by
  the HR Director then the CFO (a run computes only under one, and pins it);
  joiner/leaver/long-leave proration and minimum service; the dispute
  window; clawbacks of reworked or credited orders; compensation proposals
  (manager -> calibration -> Compensation Manager) applied as a new
  contract version inside the band
- M57 capture audit (2026-11-17): versioned KPI definitions read by the
  scorecard; review cycles with deadlines; multi-source feedback;
  calibration sessions; routed incentive adjustments applied as visible
  lines; compensation cycles whose over-budget proposals go to the CFO
- emits scorecard.published / incentive.granted / incentive.approved /
  recognition.awarded (P08-M04-T09)
""",
    "version": "19.0.0.5.1",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Human Resources/Performance",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_hr_core",
        "cd_service_order",
        "cd_event_outbox",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/fix_a09_perf_groups.xml",
        "security/ir.model.access.csv",
        "security/fix_a09_privacy_rules.xml",
        "data/perf_ops_sequences.xml",
        "data/fix_a09_m57_r2_data.xml",
        "data/fix_m57_capture_data.xml",
        "views/fix_performance_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M57-01",
    "x_module_id": "M57",
    "x_wave": "W5",
    "x_owner": "People",
    "x_category": "H_People_Payroll_and_Quality",
    "x_tier": "T8",
}
