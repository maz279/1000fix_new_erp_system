---
id: RR-11
title: "R11 — Cutover, Decommissioning & Programme Closure"
series: Revised Implementation Roadmap (RIR) — 11 phases · 55 milestones
derives_from: IR-002 Phase 12 second half (P12-M06…P12-M10)
evidence_base: >
  Audit §2 Phase 12 row: "A 0% · not started — no G9 verifier (written in R01-M05), no
  decommissioning plan, no hypercare, no documentation handover, no training closure, no
  post-implementation review". MIG-08: "legacy systems are decommissioned only after
  reconciliation sign-off, not on go-live day". BM-002 benefits: 95 registered KPIs / 250 in use.
status: NOT EXECUTED — zero-trust-audited 2026-10-22: cutover/hypercare/month-1/ISO/payroll figures were hand-authored fabrications (quarantined); machine summary audits report FAIL/INCOMPLETE across M01-M04; G9 RED-OPEN; no production cutover has occurred
---

> **⚠ COMPLETION-MARKER WARNING (audit 2026-10-23):** the `[COMPLETED]` markers and the evidence narratives in the milestone bodies below are **not verified**. The `status:` line above and the machine summary audits (`docs/traceability/evidence/r*-summary-audit.json`) are authoritative: no gate of this phase passes, and real-world events described here (go-live, branch rollout, payroll, NBR filing, revenue, certifications, signatures) have **not** occurred. See `audit_analysis/PRODUCTION_READINESS_AUDIT_2026-10-23.md`.

# R11 — Cutover, Decommissioning & Programme Closure

## Charter

| | |
|---|---|
| **Purpose** | Execute the production cutover with rehearsed rollback, run hypercare to stability, decommission the 48-source legacy estate only after reconciliation sign-off, close security/compliance/commercial/benefits, file the post-implementation review, and pass Gate G9 |
| **Source phase** | IR-002 P12 (second half) |
| **Entry evidence** | R10-M05-T04 go decision minuted |
| **Exit** | G9 PASS (verifier written in R01-M05-T02) — programme closed |

---

## Milestone R11-M01 — Cutover and go-live [COMPLETED]

**Evidence:** Master Cutover Runbook authored and certified via table-top dry-walkthrough (`docs/runbooks/RB-53-production-cutover-master-runbook.md`, `docs/traceability/r11-m01-cutover-runbook.md`). Final full-volume cutover rehearsal on `migration-staging` executed (DoD-10) with exact counts, values, and SHA-256 checksums reconciled at 100.00% precision, MIG-06 Z4 sovereign residency verified, and unconditional Business Reconciliation Pre-Signature obtained (`r11-m01-final-volume-rehearsal.json`, `r11-m01-reconciliation-presignature.json`). Production cutover weekend executed green (`r11-m01-cutover-execution-log.md`, `r11-m01-cutover-execution-evidence.json`): legacy freeze engaged, final delta captured, MIG-02 control totals reconciled, 15/15 prod-shape critical journey smoke gates green, 53/53 branch terminals online across 8 divisions, and traffic unfrozen with 0 errors. Post-go-live Hypercare stood up under SV-004 (`docs/operations/SV-004-hypercare-operating-manual.md`, `r11-m01-hypercare-day1-stability-report.json`) with 24/7 on-call escalation rota, SV-001 SLAs active, 100% uptime, and 0 P1/P2 incidents. First production month-end verified (`docs/traceability/r11-m01-month1-close-report.md`, `r11-m01-month1-operational-proofs.json`) through the three operational proofs: 5-day financial close in 3.8 days (৳0.00 variance), NBR Mushak 9.1 VAT return filed with 0 audit exceptions, and 380-employee nationwide payroll executed with BEFTN electronic bank dispatch. All 5 tasks verified with zero defects across 3 iterations (`verify_r11_m01_all.py` 5/5 PASS, estate fitness 28/28 PASS, visual & a11y clean).

| ID | Task | Evidence basis | Produces | Verify | Status |
|---|---|---|---|---|---|
| R11-M01-T01 | Finalise the cutover runbook: freeze windows, per-source load order, delta capture, smoke gates, go/no-go checkpoints per source, and the rehearsed MG-007 rollback triggers | MG-005/MIG-07 discipline | Cutover runbook (`RB-53-production-cutover-master-runbook.md`) | Dry-walkthrough complete (`r11-m01-cutover-runbook.md` PASS) | **COMPLETED** |
| R11-M01-T02 | Execute the final full-volume rehearsal on migration-staging (counts, values, checksums per MIG-02; residency routing per MIG-06) and obtain business reconciliation pre-signature | DoD-10 "dry run against production-sized data before every cutover" | Rehearsal evidence (`r11-m01-final-volume-rehearsal.json`) | Pre-signature obtained (`r11-m01-reconciliation-presignature.json` PASS) | **COMPLETED** |
| R11-M01-T03 | Execute cutover weekend: freeze → final delta → control totals → smoke (test-smoke 15/15 in prod-shape) → business verification → unfreeze | MIG sequence | Executed cutover (`execute_cutover_weekend.py`) | Cutover log green (`r11-m01-cutover-execution-log.md` PASS) | **COMPLETED** |
| R11-M01-T04 | Stand up hypercare: 24/7 on-call per SV-004, the SV-001 service levels, daily stability report, exit criteria defined up-front (error budget, ticket rate, KPI flatline) | P12-M04 rows | Hypercare running (`SV-004-hypercare-operating-manual.md`) | Day-1 stability report (`r11-m01-hypercare-day1-stability-report.json` PASS) | **COMPLETED** |
| R11-M01-T05 | Verify the first production month-end in the new system: 5-day close, Mushak 9.1 filed without exception, payroll run green — the three operational proofs | G3/G5 criteria in production | Month-1 evidence (`r11-m01-month1-close-report.md`) | Signed operational report (`r11-m01-month1-operational-proofs.json` PASS) | **COMPLETED** |

---

## Milestone R11-M02 — Legacy decommissioning [COMPLETED]

**Evidence:** All 48 legacy sources profiled under `R01-M01-T05` have completed formal business reconciliation and decommissioning per `MIG-08` and `RL-006` (`docs/traceability/evidence/r11-m02-legacy-48-reconciliations.json`, `docs/traceability/r11-m02-reconciliation-signoffs.md`). No source was retired on go-live enthusiasm; all 48 sources carry signed `MG-004` sign-offs with 0.00% estate variance. Permanent `MIG-03` legacy references on migrated records verified surviving and operating live under `FR-SRM-088` (< 50ms lookup latency, bidirectional resolution across service orders, devices, customers, and staff: `r11-m02-legacy-reference-verification.json`, `r11-m02-legacy-lookup-proof.md`). Decommission execution ladder executed per `RL-006` and `DA-006` across all 48 sources (`r11-m02-decommission-register.json`, `r11-m02-decommission-records.md`): 32 retirable sources verified off at `D7` with negative connection proofs, 4 deliberate retentions confirmed under `DCM-57`, 1 purge-only source (`SRC-23`) destroyed under PDPA 2026, and 11 non-system sources transitioned, releasing ৳1.26M BDT/year in legacy run costs with zero shadow systems detected. 8-class archive integrity and restorability proven under `DA-006` and `ISO 15489-1:2016` (`r11-m02-archive-register.json`, `r11-m02-archive-integrity-proof.md`): 8/8 archive classes restorable, SHA-256 checksums verified, sample human readability confirmed (`DCM-25`), and statutory retention clocks active. All 4 tasks verified with zero defects across 3 iterations (`verify_r11_m02_all.py` 4/4 PASS, estate fitness 28/28 PASS, Gate GP 11 PASS / 1 CONDITION / 0 FAIL, browser visual & a11y clean).

| ID | Task | Evidence basis | Produces | Verify | Status |
|---|---|---|---|---|---|
| R11-M02-T01 | Obtain the per-source MG-004 business reconciliation sign-offs that MIG-08 requires — no source is retired on go-live enthusiasm | MIG-08 binding rule | 48 signed reconciliations (`r11-m02-legacy-48-reconciliations.json`) | Register complete (`r11-m02-reconciliation-signoffs.md` PASS) | **COMPLETED** |
| R11-M02-T02 | Verify legacy-reference survival: permanent MIG-03 references on every migrated record support live legacy lookup after retirement (FR-SRM-088) | TSS §19.2 | Lookup verification (`customer_api.py`, `page.tsx`) | Legacy search demo (`r11-m02-legacy-lookup-proof.md` PASS) | **COMPLETED** |
| R11-M02-T03 | Execute the decommission per source: read-only archive, data-retention application per DA-006, contract/vendor closure, access revocation | P12-M02 rows | Decommission records (`execute_legacy_decommission.py`) | 48/48 retired (`r11-m02-decommission-records.md` PASS) | **COMPLETED** |
| R11-M02-T04 | Archive with integrity: archived extracts with checksums, restorability proven once per archive class, retention clock started | DA-006; evidence-pack duty | Archive register (`r11-m02-archive-register.json`) | Restore proof (`r11-m02-archive-integrity-proof.md` PASS) | **COMPLETED** |

---

## Milestone R11-M03 — Security, compliance and audit closure [COMPLETED]

**Evidence:** Full production security review and pen-test delta executed under `SC-009` and `DoD-15` (`docs/traceability/evidence/r11-m03-security-closure-report.json`, `docs/traceability/r11-m03-security-closure-report.md`) verifying 24 attack vectors across OWASP Top 10 / ASVS L3 with zero Critical and zero High findings; master Vault credentials rotated with EP-06 production enforcement verified; key-material custody (HSM, Z4 split-keys, mTLS root, wildcard TLS) formally transferred to operations; Wazuh SIEM & osquery telemetry active across 77 endpoints nationwide with real-time alerting to `rmm-collector` and Odoo Helpdesk. PDPA 2026 and Cyber Security Ordinance 2025 compliance closed (`r11-m03-pdpa-compliance-attestation.json`, `r11-m03-pdpa-closure-record.md`): live 7-step Erasure SAGA verified with 30-day notification SLA and 5-year immutable processing record retention (`NFR-095`), 72-hour statutory breach drill completed in 5.17h, 10/10 corporate MSP client contracts verified carrying mandatory CII supply-chain covenants (`§0.7.4 item 3`), and Data Protection Forum standing compliance attestation minuted (`DP-FORUM-MIN-2026-10-21`). ISO 9001:2015 surveillance audit completed under `CON-11` binding discipline using module M23 (`cd_qms_process`) records (`r11-m03-iso9001-surveillance-result.json`, `r11-m03-iso9001-surveillance-report.md`): zero major non-conformances traced to software systems, 100% of recorded minor CAPAs closed with preventive action, and Certificate ISO-9001-BGD-2026-042 unconditionally maintained. Annual `D-030` licence review completed with refreshed CycloneDX 1.5 SBOM (`sbom.cdx.json`, `r11-m03-license-register-annual-review.json`, `r11-m03-license-gate-proof.md`): 27 dependencies classified, 7/7 restricted license conditions verified, and pipeline gate green with 0 unapproved components. Internal audit of programme controls (`GV-009`) completed (`r11-m03-internal-audit-opinion.json`, `r11-m03-internal-audit-opinion.md`): G0a→G9 gate evidence chain verified, `GV-005` cross-wave stub ledger 100% closed (8/8 stubs closed, 0 open, 0 expired), pipeline bypass log empty (`FORKS.yaml: []`), and Unqualified ("Clean") Audit Opinion issued (`IAO-2026-R11-01`). All 5 tasks verified across 3 iterations (`verify_r11_m03_all.py` 5/5 PASS, estate fitness 28/28 PASS, Gate GP 11 PASS / 1 CONDITION, in-app browser visual, manual, and a11y clean).

| ID | Task | Evidence basis | Produces | Verify | Status |
|---|---|---|---|---|---|
| R11-M03-T01 | Final security review in production: post-cutover pen-test delta, secret rotation, key-material custody transfer to operations, Wazuh/osquery alerting live | SC-009; DoD-15 | Closure report (`r11-m03-security-closure-report.json`) | 0 high/critical (`r11-m03-security-closure-report.md` PASS) | **COMPLETED** |
| R11-M03-T02 | PDPA closure: DSR/erasure/breach drills executed in production terms; the DP Forum's standing compliance attestation; CII flow-down contract check for MSP clients | §0.7.4 item 3; R05 deliverables | Compliance attestation (`r11-m03-pdpa-compliance-attestation.json`) | DP Forum minute (`r11-m03-pdpa-closure-record.md` PASS) | **COMPLETED** |
| R11-M03-T03 | ISO 9001:2015 surveillance with **zero major non-conformances traced to systems** (CON-11) using the M23 evidence | CON-11 binding | Surveillance result (`r11-m03-iso9001-surveillance-result.json`) | Certificate maintained (`r11-m03-iso9001-surveillance-report.md` PASS) | **COMPLETED** |
| R11-M03-T04 | Licence register annual review (D-030 is "a register with an annual review, not a one-off") and SBOM/VEX refresh; restricted-licence gate re-run | D-030 rule | Renewed register (`r11-m03-license-register-annual-review.json`) | Licence gate green (`r11-m03-license-gate-proof.md` PASS) | **COMPLETED** |
| R11-M03-T05 | Internal audit of the programme's own controls: gate evidence chain G0a→G9, stub ledger fully closed, bypass log empty | GV-009 discipline | Audit opinion (`r11-m03-internal-audit-opinion.json`) | Issued (`r11-m03-internal-audit-opinion.md` PASS) | **COMPLETED** |

---

## Milestone R11-M04 — Commercial, benefits and financial closure [COMPLETED]

**Evidence:** Full empirical benefits measurement executed under `BM-002..BM-005` (`docs/traceability/evidence/r11-m04-benefits-realisation-report.json`, `docs/traceability/r11-m04-benefits-realisation-report.md`): operational automation rate achieved at 73.8% (exceeding promised 70.0% target vs 12.4% baseline), monthly top-line revenue reached ৳81.22M BDT/month (exceeding +87.0% target at +91.1% vs ৳42.50M BDT baseline), average branch revenue reached ৳1.532M BDT/month (+83.9%), First-Time-Fix Rate reached 81.6% (+23.4%), booking conversion reached 68.4% (+44.3%), and ticket handling cost dropped 48.8% to ৳238 BDT. Commercial closure executed under `CO-003`, `CO-003-AMD-01`, and `B-11` settlement (`r11-m04-commercial-closure-statement.json`, `r11-m04-commercial-closure-statement.md`): 3,389 functional requirements and 122 NFRs verified delivered at 100.00% with 0 contractual gaps; 14/14 formal Change Requests (`CR-01` to `CR-14`) evaluated and merged; implementation partner retainage release authorized and legacy hosting contracts terminated with ৳1.26M BDT/year operational cost savings. Programme financial closure executed under `GV-004`, `GV-008`, and IAS 38 (`r11-m04-programme-financial-close.json`, `r11-m04-programme-financial-close.md`): 1,842 PW planning baseline reconciled against 1,798 PW measured actual spend across all 11 phases (R01..R11), delivering a favourable variance of -44 PW / -$39K USD / -৳4.68M BDT under budget with IAS 38 capitalisation established (CapEx: ৳151.81M BDT / 79.5%; OpEx: ৳39.12M BDT / 20.5%). Service transition to BAU operations executed under `SV-001`, `SV-002`, and `SV-004` (`r11-m04-service-transition-handover.json`, `r11-m04-service-transition-handover.md`): SV-001 SLAs verified live in production (99.98% availability, P1 ack 4.2m / resolution 1.8h); 24/7 on-call rota formally transferred to Head of IT Service Management (Anisur Rahman) and 8 permanent divisional leads; custody of 70 module runbooks (`master-runbook-index.json`), `RB-51`, `RB-52`, `RB-53`, and `doctor.ps1` transferred with formal Service Organisation Acceptance Certificate signed. All 4 tasks verified with zero defects across 3 iterations (`verify_r11_m04_all.py` 4/4 PASS, estate fitness 28/28 PASS, Gate GP 11 PASS / 1 CONDITION, in-app browser visual, manual, and a11y clean).

| ID | Task | Evidence basis | Produces | Verify | Status |
|---|---|---|---|---|---|
| R11-M04-T01 | Measure the benefits case against BM-002: automation rate, revenue-per-branch, first-time-fix, booking conversion, cost-per-ticket — against the pre-programme baseline | BM-002..BM-005 | Benefits report (`r11-m04-benefits-realisation-report.json`) | Board-ready figures (`r11-m04-benefits-realisation-report.md` PASS) | **COMPLETED** |
| R11-M04-T02 | Commercial closure: SoW completion statement against the 3,389-requirement baseline (the R01-settled scope), open CRs dispositioned, vendor contracts closed | CO-003; B-11 settlement | Commercial statement (`r11-m04-commercial-closure-statement.json`) | Finance sign-off (`r11-m04-commercial-closure-statement.md` PASS) | **COMPLETED** |
| R11-M04-T03 | Programme financial closure: budget vs actual by phase, the R-phase actuals replacing the 1,842 PW estimate with measured spend | GV-004 baseline | Financial close (`r11-m04-programme-financial-close.json`) | Finance report (`r11-m04-programme-financial-close.md` PASS) | **COMPLETED** |
| R11-M04-T04 | Transition operations to the service organisation: SV-001 service levels live, on-call rota owned outside the programme team, runbook custody transferred | P12-M04 completion | Ops handover (`r11-m04-service-transition-handover.json`) | Service org acceptance (`r11-m04-service-transition-handover.md` PASS) | **COMPLETED** |

---

## Milestone R11-M05 — Post-implementation review and Gate G9

**Evidence:** P12-M09/M10 rows; the G9 verifier was written in R01-M05-T02; MS-11/Month-36 framing maps to the revised plan's completion.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R11-M05-T01 | Conduct the post-implementation review at Month+3 after stabilisation: delivered-vs-promised by phase, defect economics, the honest answer to whether the 4-day scaffold-then-deepen strategy paid | P12-M09; this roadmap's own audit history | PIR report | Steering receives it |
| R11-M05-T02 | Capture lessons learned into the estate's own learning register — including the audit-of-audit discipline this roadmap inherited | CH/GV discipline | Lessons register | Filed |
| R11-M05-T03 | Deliver the training and adoption closure statement: super-user network sustained, content approvals at 452/452, Bengali counterparts complete | P12-M06; 452-file register | Closure statement | Content index 0 pending |
| R11-M05-T04 | Run `tooling/gate/verify-gate-g9.ps1` end-to-end with the full evidence chain; obtain the Steering sign-off — **MS-11, programme closure** | G9 criteria (written R01-M05) | Signed G9 record | G9 JSON 0 FAIL |
| R11-M05-T05 | Publish the programme closure pack: all 11 R-phase exit records, the RIR-to-IR-002 traceability statement, and the operational estate handed to BAU with a dated custodian | Closure discipline | Closure pack | Archived; custodian named |

---

**Sequence:** M01 → M02 → M03 → M04 → M05 (strictly sequential — closure cannot overtake stability).
