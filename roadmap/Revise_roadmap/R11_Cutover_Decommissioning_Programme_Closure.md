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
status: PLANNED — evidence-derived
---

# R11 — Cutover, Decommissioning & Programme Closure

## Charter

| | |
|---|---|
| **Purpose** | Execute the production cutover with rehearsed rollback, run hypercare to stability, decommission the 48-source legacy estate only after reconciliation sign-off, close security/compliance/commercial/benefits, file the post-implementation review, and pass Gate G9 |
| **Source phase** | IR-002 P12 (second half) |
| **Entry evidence** | R10-M05-T04 go decision minuted |
| **Exit** | G9 PASS (verifier written in R01-M05-T02) — programme closed |

---

## Milestone R11-M01 — Cutover and go-live

**Evidence:** No cutover plan exists; the migration apparatus (loaders from R02-M04/R03-M01, rehearsal procedure from R10-M05-T02) is the entry state; MIG-07 rollback must be rehearsed, not just documented.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R11-M01-T01 | Finalise the cutover runbook: freeze windows, per-source load order, delta capture, smoke gates, go/no-go checkpoints per source, and the rehearsed MG-007 rollback triggers | MG-005/MIG-07 discipline | Cutover runbook | Dry-walkthrough complete |
| R11-M01-T02 | Execute the final full-volume rehearsal on migration-staging (counts, values, checksums per MIG-02; residency routing per MIG-06) and obtain business reconciliation pre-signature | DoD-10 "dry run against production-sized data before every cutover" | Rehearsal evidence | Pre-signature obtained |
| R11-M01-T03 | Execute cutover weekend: freeze → final delta → control totals → smoke (test-smoke 15/15 in prod-shape) → business verification → unfreeze | MIG sequence | Executed cutover | Cutover log green |
| R11-M01-T04 | Stand up hypercare: 24/7 on-call per SV-004, the SV-001 service levels, daily stability report, exit criteria defined up-front (error budget, ticket rate, KPI flatline) | P12-M04 rows | Hypercare running | Day-1 stability report |
| R11-M01-T05 | Verify the first production month-end in the new system: 5-day close, Mushak 9.1 filed without exception, payroll run green — the three operational proofs | G3/G5 criteria in production | Month-1 evidence | Signed operational report |

---

## Milestone R11-M02 — Legacy decommissioning

**Evidence:** 48 legacy sources profiled (R01-M01-T05); MIG-08 forbids decommissioning before reconciliation sign-off; the two live trackers and paper flows (withdrawn in Dhaka at G2, nationally by now) are in scope.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R11-M02-T01 | Obtain the per-source MG-004 business reconciliation sign-offs that MIG-08 requires — no source is retired on go-live enthusiasm | MIG-08 binding rule | 48 signed reconciliations | Register complete |
| R11-M02-T02 | Verify legacy-reference survival: permanent MIG-03 references on every migrated record support live legacy lookup after retirement (FR-SRM-088) | TSS §19.2 | Lookup verification | Legacy search demo |
| R11-M02-T03 | Execute the decommission per source: read-only archive, data-retention application per DA-006, contract/vendor closure, access revocation | P12-M02 rows | Decommission records | 48/48 retired |
| R11-M02-T04 | Archive with integrity: archived extracts with checksums, restorability proven once per archive class, retention clock started | DA-006; evidence-pack duty | Archive register | Restore proof |

---

## Milestone R11-M03 — Security, compliance and audit closure

**Evidence:** P12-M07 rows; the compliance estate (PDPA operational from R05, ISO 9001 support from R06, licence register D-030 annual review) needs its closing verification; the Cyber Security Ordinance 2025 supply-chain duty applies if any MSP client is CII-designated.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R11-M03-T01 | Final security review in production: post-cutover pen-test delta, secret rotation, key-material custody transfer to operations, Wazuh/osquery alerting live | SC-009; DoD-15 | Closure report | 0 high/critical |
| R11-M03-T02 | PDPA closure: DSR/erasure/breach drills executed in production terms; the DP Forum's standing compliance attestation; CII flow-down contract check for MSP clients | §0.7.4 item 3; R05 deliverables | Compliance attestation | DP Forum minute |
| R11-M03-T03 | ISO 9001:2015 surveillance with **zero major non-conformances traced to systems** (CON-11) using the M23 evidence | CON-11 binding | Surveillance result | Certificate maintained |
| R11-M03-T04 | Licence register annual review (D-030 is "a register with an annual review, not a one-off") and SBOM/VEX refresh; restricted-licence gate re-run | D-030 rule | Renewed register | Licence gate green |
| R11-M03-T05 | Internal audit of the programme's own controls: gate evidence chain G0a→G9, stub ledger fully closed, bypass log empty | GV-009 discipline | Audit opinion | Issued |

---

## Milestone R11-M04 — Commercial, benefits and financial closure

**Evidence:** P12-M08 rows; BM-002 registers 95 KPIs with 250 in use; the programme's business case promised 70% automation and 87% revenue growth — these are measured claims now.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R11-M04-T01 | Measure the benefits case against BM-002: automation rate, revenue-per-branch, first-time-fix, booking conversion, cost-per-ticket — against the pre-programme baseline | BM-002..BM-005 | Benefits report | Board-ready figures |
| R11-M04-T02 | Commercial closure: SoW completion statement against the 3,389-requirement baseline (the R01-settled scope), open CRs dispositioned, vendor contracts closed | CO-003; B-11 settlement | Commercial statement | Finance sign-off |
| R11-M04-T03 | Programme financial closure: budget vs actual by phase, the R-phase actuals replacing the 1,842 PW estimate with measured spend | GV-004 baseline | Financial close | Finance report |
| R11-M04-T04 | Transition operations to the service organisation: SV-001 service levels live, on-call rota owned outside the programme team, runbook custody transferred | P12-M04 completion | Ops handover | Service org acceptance |

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
