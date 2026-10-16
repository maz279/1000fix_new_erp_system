---
id: RR-06
title: "R06 — People, Payroll & Quality at Full Depth"
series: Revised Implementation Roadmap (RIR) — 11 phases · 55 milestones
derives_from: IR-002 Phase 8 (P08-M01…P08-M10)
evidence_base: >
  G5 re-run 2026-10-15: 9 PASS · 1 CONDITION (G5-9 gate profile — performance 1.5× + DR drill);
  cd_payroll_bd implements Labour (Amendment) Act 2026 rates (gratuity 30/45-day bands, PF) but
  100% coverage on payroll calculation paths is UNMEASURED (no coverage artefacts exist);
  biometric INT-041, BEFTN INT-005, Mayan EDMS and MeshCentral/RustDesk/Wazuh stacks are
  compose-defined but unwired; stubs M02→M22/M55, M31→M22/M23 opened in R03 carry expiries
  targeting this phase.
status: PLANNED — evidence-derived
---

# R06 — People, Payroll & Quality at Full Depth

## Charter

| | |
|---|---|
| **Purpose** | Make payroll — the estate's highest-consequence financial path — measured at 100% coverage and BEFTN-live; close every stub opened in Waves 2–4 under its expiry; stand up the MSP and quality platforms; complete the auditor app; run the G5 gate profile that is the phase's one open condition |
| **Source phase** | IR-002 P08 |
| **Entry evidence** | G5-9 CONDITION; audit V-5 (coverage unmeasured); Appendix E stub register |
| **Exit** | G5 10/10 PASS including the gate profile; zero stubs past expiry |

---

## Milestone R06-M01 — M21 Core HR complete

**Evidence:** `cd_hr_core` exists (7 py) as the full-HR extension beyond the W1 master; org structure, Labour Act leave and employment artefacts unverified at depth; KPI-090 unmeasured.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R06-M01-T01 | Install Odoo `hr_holidays` + the OCA hr set (vendored, unconsumed); build statutory Bangladesh leave entitlements with citations verified current (DoD-17) | V-2; P08-M01-T01/T04 | HR layer + leave model | Entitlement tests |
| R06-M01-T02 | Build Labour Act employment-contract artefacts on M24 templates (the +52% Category H statutory density lives here) | P08-M01-T05 | Employment artefacts | Legal sign-off |
| R06-M01-T03 | Verify the W1 joiner/mover/leaver events still drive M29 provisioning at full scale; instrument **KPI-090 (zero orphaned accounts >24 h)** with the leaver ≤1 h Keycloak deprovisioning measured | P08-M01-T06; KPI-090 never instrumented | KPI live in M25 | Measured KPI-090 = 0 |
| R06-M01-T04 | Route all employee PII (NID/TIN/biometric templates) through the residency service; FF-09 scan over the HR tables | P08-M01-T07 | Residency conformance | FF-09 green on HR models |
| R06-M01-T05 | Take M57 performance/incentives to depth (technician scorecard surfaced in P02, incentive engine feeding payroll with 100% coverage, compensation banding with **T5 field-level permissions** negative-tested) and build **M35 marketing/campaigns** (40 reqs) consuming M10's campaign hooks from R03 | P08-M04 rows; cd_performance/cd_campaign exist as scaffolds; audit scaffolds register | M57 + M35 at depth | Incentive CI job 100%; campaign e2e test |

---

## Milestone R06-M02 — M55 Attendance, scheduling, and the stub closures begin

**Evidence:** `cd_attendance` scaffold; the M02→M55 availability stub (opened R03-M03-T05) returns "available within working calendar" from M30; biometric devices INT-041 are S3-classified and unwired.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R06-M02-T01 | Build time & attendance on Odoo `hr_attendance` with the working-time compliance rules (hours, overtime, rest) per the amended Labour Act | P08-M02-T01/T04 | Attendance module | Compliance tests |
| R06-M02-T02 | Integrate INT-041 biometric devices with templates routed through Z4 (S3 residency class — never the regional store) | P08-M02-T02/T08 | Biometric ingest | FF-09 green on templates |
| R06-M02-T03 | Build shift/roster management and **close the M02→M55 stub**: dispatch availability now reads the real roster | Appendix E; stub from R03 | Stub closed in GV-005 | Dispatch eligibility test |
| R06-M02-T04 | Build the attendance lock payroll depends on (journey 13's first gate) and wire P02's geofenced clock-in into it | P08-M02-T05/T06 | Lock mechanism | Lock→payroll ordering test |
| R06-M02-T05 | Migrate attendance opening balances only (sign-in books; history not migrated per the standing ruling) | P08-M02-T07 | Balances loaded | Count reconciled |

---

## Milestone R06-M03 — M56 Payroll: statutory completion, BEFTN, and the 100% gate

**Evidence:** `cd_payroll_bd` (264 LOC) + `services/payroll-engine` (2 py) exist; income tax, BEFTN batch-window modelling and Bengali payslip reference images are ahead; DoD-03 requires 100% on every payroll path — currently unmeasurable because no coverage harness ran before R01-M04.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R06-M03-T01 | Implement Bangladesh income-tax calculation and withholding with verified-current citations | P08-M03-T03 | Tax rules | Citation register with dates |
| R06-M03-T02 | Complete the Labour (Amendment) Act 2026 set: PF contribution structure/trust governance/reporting timelines; gratuity 30/45-day bands; voluntary-resignation compensation 7/15/30 — each with tests at 100% | P08-M03-T04; §0.7.4 item 1 | Statutory rules | CI payroll job **100%** |
| R06-M03-T03 | Integrate INT-005 BEFTN with the **batch cut-off modelled in the payroll calendar** (Sunday–Thursday week; Friday/holiday rollover) — a missed cut-off pays 500+ staff late | P08-M03-T05 | BEFTN integration | Cut-off negative test |
| R06-M03-T04 | Generate Bengali payslips compared against committed conjunct-shaping reference images (TR-07 names payslips explicitly) | P08-M03-T06 | Payslip rendering | Reference-image match |
| R06-M03-T05 | Run journey 13 end to end (lock → calc → approve → BEFTN → payslips → GL posting) and negative-test the approval chain SoD | P08-M03-T09; journey 13 | Journey evidence | Nightly spec green |

---

## Milestone R06-M04 — M22/M23 quality and M05 MSP platforms

**Evidence:** `cd_competency`/`cd_qms_process` scaffolds; the certification stubs (M02→M22, M31→M22) and QC stubs (M31→M23, plus M34→M23, M42→M23 from R05) all expire here; OCA `management-system` (33 modules) vendored-unconsumed; MeshCentral/RustDesk/Wazuh/osquery are stack-named but undeployed.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R06-M04-T01 | Build the competency/certification register with expiry tracking and **FR-LMS-039 dispatch eligibility**; close the M02→M22 and M31→M22 stubs — retrofit the blocking check into the live assignment path and negative-test that an uncertified technician is unassignable | Appendix E; G5-4 standard | Stubs closed; eligibility blocks | Negative test red |
| R06-M04-T02 | Build M23 NCR/root-cause/CAPA on OCA `management-system`; transfer QC checklist ownership from M01; close the M31→M23, M34→M23 and M42→M23 stubs | P08-M06 rows; stub register | Stubs closed | GV-005 all rows closed |
| R06-M04-T03 | Audit the stub ledger: **no stub outlived its expiry** — any that did is reported as an incident, not a task | P08-M05-T06 discipline | Stub audit report | 0 expired stubs |
| R06-M04-T04 | Deploy MeshCentral/RustDesk, Wazuh and osquery; implement the `rmm-collector` service to design depth; alert-to-ticket automation with SLA tracking (journey 6) | P08-M07 rows; rmm-collector exists at 2 py | MSP platform | Journey 6 nightly |
| R06-M04-T05 | Take the L6 RMM-agent pilot decision (approve with OSS review, or drop) and generate the monthly MSP service report in Bengali and English | P08-M07-T08 | Minuted decision + report | Client-ready report |

---

## Milestone R06-M05 — P11 auditor app, Mayan EDMS, and the G5 gate profile

**Evidence:** auditor app is a 1-file Flutter shell; Mayan EDMS is stack-named only; G5-9 (gate profile: performance at 1.5× peak + DR drill) is the sole open G5 condition; M45 calibration and M46 vehicle-assignment deferrals from W2 land here.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R06-M05-T01 | Build the P11 auditor app on `fix_offline` (the third consumer — proves the engine contract): audit checklists offline, field NCR raising, branch self-audit; run the L12 suite against it | P08-M09-T01..T04 | Full auditor app | L12 pass |
| R06-M05-T02 | Deploy Mayan EDMS; run the document migration with control totals; verify M24 retention/legal-hold policy applies across **both** stores (kernel stays authoritative) | P08-M09-T05..T07 | Mayan live + migrated | Dual-store policy test |
| R06-M05-T03 | Deliver the W2 deferrals: M45 test-equipment calibration (closing the M31 downgrade) and M46 fleet→dispatch vehicle assignment | P08-M08-T02/T04 | Calibration + assignment | Deferral register closed |
| R06-M05-T04 | Run the **G5 gate profile**: performance at 1.5× peak (DoD-14) and the PE-007 DR drill with recorded evidence | G5-9 CONDITION — the only open item | Perf + DR evidence | Both pass |
| R06-M05-T05 | Re-run `verify-gate-g5.ps1`: target 10/10 PASS; publish the gate report | G5 discipline | Signed G5 record | G5 JSON 0 conditions |

---

**Sequence:** M01 → M02 → M03 → M04 → M05 (M04's stub closures depend on M02-T03; M05 requires all).
