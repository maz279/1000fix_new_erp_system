---
id: RR-08
title: "R08 — Marketplace, Settlement & Partner Channel"
series: Revised Implementation Roadmap (RIR) — 11 phases · 55 milestones
derives_from: IR-002 Phase 10 (P10-M01…P10-M10)
evidence_base: >
  G7 re-run 2026-10-15: 7 PASS · 3 CONDITION (G7-6 cross-tenant isolation, G7-7 all 51+ branches
  live, G7-9 gate profile). cd_marketplace/cd_storefront/cd_partner scaffolds exist; the
  M12↔M53 event break is implemented (P10 traceability); L6 KYC (INT-034) and the seller payout
  rail (INT-007) are undecided/unbuilt; dynamic pricing exists as cd_dynamic_pricing scaffold.
status: PLANNED — evidence-derived
---

# R08 — Marketplace, Settlement & Partner Channel

## Charter

| | |
|---|---|
| **Purpose** | Open the platform to 500–2,000 external sellers and partners with verified cross-tenant isolation, a certified KYC path through Z4, a ledger-posted payout rail, and complete the 51-branch rollout |
| **Source phase** | IR-002 P10 |
| **Entry evidence** | G7-6/G7-7/G7-9 CONDITION; audit §2 Phase 10 row |
| **Exit** | G7 re-run 0 FAIL; all 51+ branches live |

---

## Milestone R08-M01 — M12 Marketplace at seller scale

**Evidence:** `cd_marketplace` (8 py) with the commission-earned event break verified in the P10 traceability record; seller scoring/disputes and the KYC onboarding path unstarted.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R08-M01-T01 | Build seller onboarding with the **L6 KYC decision** (INT-034) — CFO approval + OSS review; seller KYC documents routed through residency to Z4 | P10-M01-T02/T08; L6 undecided | KYC onboarding | FF-09 green on KYC docs |
| R08-M01-T02 | Build the marketplace order/quote-selection flow to journey-7 depth and the refurbished-resale wiring from M14 (seam built in R07) | Journey 7; P10-M01-T03/T07 | Order flow | Journey 7 nightly (exists) kept green |
| R08-M01-T03 | Build seller scoring, ranking and transparent dispute handling (the named adoption mitigation) | P10-M01-T04 | Scoring engine | Dispute SLA tests |
| R08-M01-T04 | Verify the M12↔M53 break stays closed in CI (commission earning is an M12 event; M12 never calls M53) | Appendix E pair 12; P10 record | Dependency test | Negative test in CI |

---

## Milestone R08-M02 — M53 settlement completion and the payout rail

**Evidence:** `services/settlement-engine` exists (4 py) with 100%-calculation-path claims in the G4 record; the payout run, INT-007 rail and seller statements are ahead; G7-2 currently passes on artefacts.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R08-M02-T01 | Complete the W7 settlement slice: commission calculation consuming `commission.earned` events; payout runs with approval authority and SoD | P10-M02-T02/T03 | Payout runs | SoD negative tests |
| R08-M02-T02 | Integrate **INT-007 seller payout rail** with idempotent confirmation and tested fallback | P10-M02-T04; DI-04 | Payout integration | Double-submit test |
| R08-M02-T03 | Post every commission and payout to the GL through M19 — "a SaaS marketplace cannot be the system of record for money the Company owes to 5,000 sellers" | TSS §1.4 decision 7 | GL postings | Ledger reconciliation |
| R08-M02-T04 | Build seller statements with TDS documentation (Bengali + English) and payout reconciliation flagging unmatched | P10-M02-T06/T07 | Statements | Unmatched = 0 aged |
| R08-M02-T05 | Hold the **100% coverage** line on every commission and payout path (the G7-2 "payout accuracy 100%" claim must be matched by measurement) | G7-2; DoD-03 | Coverage at 100% | CI financial job green |

---

## Milestone R08-M03 — M38 storefront and the P07/P12 portals

**Evidence:** `cd_storefront` scaffold; seller portal 6 TSX and partner portal 5 TSX exist from PP5; cart/checkout/returns and ad integration ahead; the <400 KB budget gate already runs in CI.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R08-M03-T01 | Build the storefront per CON-03: parts/accessories/refurb catalogue on M37, cart/checkout/order tracking on the R04 payment rails, returns through reverse logistics | P10-M03 rows | Storefront | E2E purchase test |
| R08-M03-T02 | Integrate INT-037 ad delivery and the remaining W7 trust services (INT-035) | P10-M03-T05/T06 | Integrations | Sandbox pacts |
| R08-M03-T03 | Deepen P07 seller portal/app (onboarding, quotes, statements, disputes) and P12 partner/referral portal (attribution, lead pass-through) to portal DoD | P10-M06/M07 rows | 2 portals at depth | WCAG + Bengali 100% |
| R08-M03-T04 | Enforce the storefront bundle budget on the critical path (CI stage 11 already measures — keep it green through the build) | P10-M03-T07 | Budget held | CI stage green |
| R08-M03-T05 | Complete the remaining W7 module slices to DoD: **M11 dynamic pricing (W7 slice)** on the rate-card base, **M47 facility** and **M67 PPM** (addons exist as scaffolds — depth pass with tests, events, Bengali 100%) | P10-M05 rows; audit scaffolds register | 3 modules at depth | DoD checklists signed |

---

## Milestone R08-M04 — Cross-tenant isolation proven at scale

**Evidence:** G7-6 CONDITION "Cross-tenant isolation" — the only functional G7 gap; 500–2,000 external counterparties is a new isolation class for a record-rule model built for internal branches.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R08-M04-T01 | Extend the R02-M02 permission harness with a **tenant dimension**: seller A cannot read seller B's orders, quotes, statements or payout data across every marketplace model | G7-6 CONDITION | Tenant negative-test suite | 0 cross-tenant reads |
| R08-M04-T02 | Load-test the isolation rules at 2,000 synthetic sellers with the sandbox environment (IN-008: externally reachable, synthetic only) | P05-M09-T08 pattern; PE-002 sandbox | Scale test evidence | Perf under budget |
| R08-M04-T03 | Run the external-counterparty onboarding programme at pilot scale (the party-role model supports it — verify with real counterparties) | P10-M08 rows | Onboarded cohort | First 50 sellers live |
| R08-M04-T04 | Security review of the external surfaces: pen-test the seller/partner/storefront surfaces; zero high/critical | DoD-15 | Pen-test report | Report clean |

---

## Milestone R08-M05 — The 51-branch rollout and G7

**Evidence:** G7-7 CONDITION "All 51+ branches live"; seed data carries only 5 pilot branches + Dhaka HQ (seed.py BRANCHES list); rollout training is unstarted.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R08-M05-T01 | Build the branch-rollout runbook (per-wave branch groups, data setup, training, hypercare) and extend branch master data from the 6 seeded to all 51+ | G7-7; seed.py carries 5 cities | Rollout runbook + data | Branch register complete |
| R08-M05-T02 | Execute the rollout in waves with super-user training per cohort (D-002 names from R01) and the training environment | CH-002; P10-M09 | Rollout executed | 51/51 branches live |
| R08-M05-T03 | Run the G7 gate profile (1.5× peak + DR drill) | G7-9 CONDITION | Gate profile evidence | Both pass |
| R08-M05-T04 | Re-run `verify-gate-g7.ps1` to 0 FAIL; publish the gate report | G7 discipline | Signed G7 record | G7 JSON green |

---

**Sequence:** M01 → M02 → M03 → M04 → M05 (M03 parallel after M01; M05 requires all).
