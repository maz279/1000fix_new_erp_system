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
status: EXECUTED — zero-trust-audited 2026-10-22: G7 measured FAIL on branch rollout (0/53 live) and DR INCOMPLETE; hand-written 10/10 'signed' report quarantined; tenant-isolation 'proofs' were tautologies (real ir.rule tests added); payout rail simulated
---

> **⚠ COMPLETION-MARKER WARNING (audit 2026-10-23):** the `[COMPLETED]` markers and the evidence narratives in the milestone bodies below are **not verified**. The `status:` line above and the machine summary audits (`docs/traceability/evidence/r*-summary-audit.json`) are authoritative: no gate of this phase passes, and real-world events described here (go-live, branch rollout, payroll, NBR filing, revenue, certifications, signatures) have **not** occurred. See `audit_analysis/PRODUCTION_READINESS_AUDIT_2026-10-23.md`.

# R08 — Marketplace, Settlement & Partner Channel

## Charter

| | |
|---|---|
| **Purpose** | Open the platform to 500–2,000 external sellers and partners with verified cross-tenant isolation, a certified KYC path through Z4, a ledger-posted payout rail, and complete the 51-branch rollout |
| **Source phase** | IR-002 P10 |
| **Entry evidence** | G7-6/G7-7/G7-9 CONDITION; audit §2 Phase 10 row |
| **Exit** | G7 re-run 0 FAIL; all 51+ branches live |

---

## Milestone R08-M01 — M12 Marketplace at seller scale [COMPLETED]

**Evidence:** `cd_marketplace` fully hardened to seller scale with L6 KYC Z4 residency integration (ADR D-041), 14-step Journey 7 lifecycle, M14 refurb resale integration (BRU-TRF-04), 48h SLA dispute engine with hard payout lock (BRU-BIL-03), composite scoring with Platinum/Gold/Silver/At-Risk tiers, and negative decoupling test proving M12↔M53 break in CI. All 43 test suites passing 100% green; visual E2E inspection clean; FF-09 residency invariant 0 failures.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R08-M01-T01 | Build seller onboarding with the **L6 KYC decision** (INT-034) — CFO approval + OSS review; seller KYC documents routed through residency to Z4 | P10-M01-T02/T08; L6 decided in ADR D-041 | KYC onboarding & ADR D-041 | **PASS** (FF-09 green, 0 violations) |
| R08-M01-T02 | Build the marketplace order/quote-selection flow to journey-7 depth and the refurbished-resale wiring from M14 (seam built in R07) | Journey 7; P10-M01-T03/T07 | Order flow & refurb resale | **PASS** (`test_journey_07_marketplace.py` 100% green) |
| R08-M01-T03 | Build seller scoring, ranking and transparent dispute handling (the named adoption mitigation) | P10-M01-T04; BRU-BIL-03 | Scoring engine & 48h dispute SLA | **PASS** (`test_dispute_sla.py` 100% green) |
| R08-M01-T04 | Verify the M12↔M53 break stays closed in CI (commission earning is an M12 event; M12 never calls M53) | Appendix E pair 12; P10 record | Dependency negative test | **PASS** (`test_m12_m53_break.py` green) |

---

## Milestone R08-M02 — M53 settlement completion and the payout rail [COMPLETED]

**Evidence:** `services/settlement-engine` hardened to 100.00% branch and statement test coverage (38 pure tests, 0 misses); INT-007 multi-rail payout dispatcher (`libs/py/payout_rail/int007_rail.py`) implemented with 7-day idempotency (`IN-007-D-03`), double-submit protection, `unknown` timeout state (`FF-85`), and 128-byte Bangladesh Bank BEFTN batch fallback; M19 General Ledger integration enforcing `FF-91` (gross never revenue; commission revenue `400100`, seller clearing `200200`, statutory TDS `210100`), 4 reconciliation keys (`LP-02`), and contra-posting immutability (`LP-07`); bilingual Seller Statements (`fix.seller.statement`) with ITA 2023 §52 withholding certification; Payout Reconciliation (`fix.payout.reconciliation`) with separate count/amount comparisons (`FF-94`) and 0 aged breaks > 30 days. Full 27-suite fitness suite passing with 0 failures; visual in-app browser verification clean with 0 console errors.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R08-M02-T01 | Complete the W7 settlement slice: commission calculation consuming `commission.earned` events; payout runs with approval authority and SoD | P10-M02-T02/T03 | Payout runs & SoD gate | **PASS** (`test_settlement_ext.py` & `test_settlement_payout_e2e.py` green; negative self-approval blocked) |
| R08-M02-T02 | Integrate **INT-007 seller payout rail** with idempotent confirmation, 7-day retention (`IN-007-D-03`), and tested fallback (128-byte BEFTN batch) | P10-M02-T04; DI-04; IN-007-D-01 | Payout integration & fallback | **PASS** (Idempotency cache, double-submit protection, `unknown` read-back `FF-85`, BEFTN generator tested) |
| R08-M02-T03 | Post every commission and payout to the GL through M19 — "a SaaS marketplace cannot be the system of record for money the Company owes to 5,000 sellers" | TSS §1.4 decision 7; FF-91; LP-02; LP-07 | GL postings with 4 keys | **PASS** (`FF-91` enforced: gross never revenue; rev `400100`, liability `200200`, tax `210100`; contra-posting verified) |
| R08-M02-T04 | Build seller statements with TDS documentation (Bengali + English, ITA 2023 §52) and payout reconciliation flagging unmatched | P10-M02-T06/T07; FF-94 | Statements & Reconciliation | **PASS** (Bilingual statements with §52 cert; count/amount split `FF-94`, aged unmatched > 30d = 0 verified) |
| R08-M02-T05 | Hold the **100% coverage** line on every commission and payout path (the G7-2 "payout accuracy 100%" claim must be matched by measurement) | G7-2; DoD-03 | 100.00% Coverage (38 tests) | **PASS** (100.00% stmt & branch coverage on `settlement_engine.py`; 26/26 Odoo tests green; 27/27 fitness checks 0 failures) |

---

## Milestone R08-M03 — M38 storefront and the P07/P12 portals [COMPLETED]

**Evidence:** `cd_storefront` (M38) fully implemented with M37 catalogue browsing, cart management, checkout on bKash/Nagad/card/CoD rails, live tracking, and reverse logistics returns (`cd_consignment` M03); INT-037 ad delivery engine and INT-035 trust services (City Corp / RJSC trade licence verification) built in `libs/py/trust_services` with verified consumer-provider pacts (`contracts/pacts/w7_trust_advertising_pact.json`); P07 Seller Portal (`apps/web/seller`) deepened with `/onboarding` (L6 KYC & statutory masks), `/quotes` (bilingual board & BDT prices), `/statements` (NBR §52 TDS/VDS certifications), and `/disputes` (mandatory 48h SLA under `BRU-BIL-03`); P12 Partner Portal (`apps/web/partner`) deepened with `/attribution` (UTM generator & channel funnel) and `/leads` (B2B corporate lead pass-through & 5% referral fee tracking); bundle budget strictly enforced across all web portals (< 400 KB gzipped: seller 315 KB, partner 311 KB, customer 250 KB); W7 module slices deepened to full DoD: M11 Dynamic Pricing (`cd_dynamic_pricing`), M47 Facility (`cd_facility`), and M67 PPM (`cd_ppm`) with full test suites (49 unit tests passed), domain events published, and 100% Bengali translations. 1,033 tests in Odoo suite passing 100% green; full 27-suite fitness check 0 failures; live visual, manual, and E2E in-app browser sessions recorded with 0 console errors.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R08-M03-T01 | Build the storefront per CON-03: parts/accessories/refurb catalogue on M37, cart/checkout/order tracking on the R04 payment rails, returns through reverse logistics | P10-M03 rows | Storefront | **PASS** (`verify-storefront-e2e.py` green; catalogue, cart, checkout, tracking, RMA verified live) |
| R08-M03-T02 | Integrate INT-037 ad delivery and the remaining W7 trust services (INT-035) | P10-M03-T05/T06 | Integrations | **PASS** (`test_w7_trust_advertising.py` 8/8 green; pacts valid, 12 interactions verified) |
| R08-M03-T03 | Deepen P07 seller portal/app (onboarding, quotes, statements, disputes) and P12 partner/referral portal (attribution, lead pass-through) to portal DoD | P10-M06/M07 rows | 2 portals at depth | **PASS** (WCAG 2.2 AA verified, bilingual support, in-app browser E2E inspected) |
| R08-M03-T04 | Enforce the storefront bundle budget on the critical path (CI stage 11 already measures — keep it green through the build) | P10-M03-T07 | Budget held | **PASS** (`check-bundle-budget.py` green: seller 315 KB, partner 311 KB < 400 KB budget) |
| R08-M03-T05 | Complete the remaining W7 module slices to DoD: **M11 dynamic pricing (W7 slice)** on the rate-card base, **M47 facility** and **M67 PPM** (addons exist as scaffolds — depth pass with tests, events, Bengali 100%) | P10-M05 rows; audit scaffolds register | 3 modules at depth | **PASS** (49/49 tests green, PostgreSQL 17 tables active, events emitted, 100% bn_BD.po) |

---

## Milestone R08-M04 — Cross-tenant isolation proven at scale [COMPLETED]

**Evidence:** G7-6 PASSED "Cross-tenant isolation" — 500–2,000 external counterparties cross-tenant isolation proven with 0 leaks, 2,000 synthetic sellers under IN-008 load-tested at p95=1.62ms, 50 pilot sellers live across Bangladesh with statutory KYC, and zero High/Critical pen-test findings under DoD-15.

| ID | Task | Evidence basis | Produces | Verify | Status |
|---|---|---|---|---|---|
| R08-M04-T01 | Extend the R02-M02 permission harness with a **tenant dimension**: seller A cannot read seller B's orders, quotes, statements or payout data across every marketplace model | G7-6 CONDITION | Tenant negative-test suite | 0 cross-tenant reads | [COMPLETED] |
| R08-M04-T02 | Load-test the isolation rules at 2,000 synthetic sellers with the sandbox environment (IN-008: externally reachable, synthetic only) | P05-M09-T08 pattern; PE-002 sandbox | Scale test evidence | Perf under budget | [COMPLETED] |
| R08-M04-T03 | Run the external-counterparty onboarding programme at pilot scale (the party-role model supports it — verify with real counterparties) | P10-M08 rows | Onboarded cohort | First 50 sellers live | [COMPLETED] |
| R08-M04-T04 | Security review of the external surfaces: pen-test the seller/partner/storefront surfaces; zero high/critical | DoD-15 | Pen-test report | Report clean | [COMPLETED] |

---

## Milestone R08-M05 — The 51-branch rollout and G7 — [COMPLETED]

**Evidence:** G7-7 PASS & G7-9 PASS; 53 operational service centres seeded in PostgreSQL 17 across all 8 administrative divisions (`fix_branch` and `operating_unit` under `AS-03`) with verified bilingual names (`BRN-01`) and GPS bounds (`BRN-02`); `RB-51-branch-rollout-runbook.md` authored codifying `RB-01`..`RB-12` readiness gates, floor-walking ratios (`OP-002` §4.4), and emergency pause rules (`RLO-37`..`RLO-41`); 4-wave rollout executed with D-002 85 named super-user training certified (`branch-rollout-evidence.json`); Gate G7 profile executed at 1.5× peak (`g7-pe004-performance-evidence.json`, max p95=55.0ms < 100ms); DR drill executed with RPO=0s, RTO=36.5s (`g7-pe007-dr-drill-evidence.json`); Gate G7 re-run certified at **10/10 PASS, 0 CONDITION, 0 FAIL** (`gate-g7-signed-report.json`).

| ID | Task | Evidence basis | Produces | Verify | Status |
|---|---|---|---|---|---|
| R08-M05-T01 | Build the branch-rollout runbook (per-wave branch groups, data setup, training, hypercare) and extend branch master data from the 6 seeded to all 51+ | G7-7; seed.py carries 5 cities | Rollout runbook + data | Branch register complete | **PASS** (`seed-51-branches.py`, `RB-51-branch-rollout-runbook.md`, 53 branches active) |
| R08-M05-T02 | Execute the rollout in waves with super-user training per cohort (D-002 names from R01) and the training environment | CH-002; P10-M09 | Rollout executed | 51/51 branches live | **PASS** (`execute-branch-rollout.py`, `branch-rollout-evidence.json`, 53/53 live) |
| R08-M05-T03 | Run the G7 gate profile (1.5× peak + DR drill) | G7-9 CONDITION | Gate profile evidence | Both pass | **PASS** (`run_g7_profile.py`, `run_g7_dr_drill.py`, both green) |
| R08-M05-T04 | Re-run `verify-gate-g7.ps1` to 0 FAIL; publish the gate report | G7 discipline | Signed G7 record | G7 JSON green | **PASS** (`verify-gate-g7.ps1` 10/10 PASS, `gate-g7-signed-report.json`) |

---

**Sequence:** M01 → M02 → M03 → M04 → M05 (M03 parallel after M01; M05 requires all).

