---
id: CG-014
title: Content Metrics and Effectiveness Measurement
project: 1000FiX ERP System v2.0
content_type: Standard
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Content Lead
author: Programme Content Lead with BI Lead
reviewers: [Content Design Lead, Localisation Lead, L&D Lead, Support Lead, BI Lead]
approver: Programme Content Lead
purpose: >
  Defines how content success is measured, so that content budget is defended with evidence
  rather than assertion and weak content is found before users complain about it. Content is
  the largest unfunded item in the programme; without measurement it will be the first thing
  cut and the last thing anyone can prove was worth funding.
traces_to: [06-02 KPI Benefits and Acceptance Criteria, RP-001, 04-00 portal KPIs, AF-09, CG-002 §9]
priority: P2
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI, Benefits & Acceptance Criteria
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 — per-portal KPI tables P01–P12
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §5 NFR-075 (agent competence in ≤ 4 hours), NFR-076 (intake ≤ 3 minutes)
    verified: 2026-08-15
supersedes: none
review_due: 2027-02-15
---

# CG-014 — Content Metrics and Effectiveness Measurement

> **Content is the largest unfunded item in this programme** — 520–775 person-weeks, absent from
> the business case (`AF-09`). Unfunded work that cannot demonstrate its effect gets cut first
> and misses its deadlines quietly.
>
> This file exists so that two questions have evidence-based answers: **"is the content
> working?"** and **"was it worth what it cost?"**

---

## 1. Principles

| # | Principle |
|---|---|
| **ME-01** | **Measure outcomes, not output.** Files written is a progress measure, not a success measure |
| **ME-02** | **Every content metric maps to a programme KPI** in `06-02` or a portal KPI in `04-00`. Content does not invent its own success criteria |
| **ME-03** | **Baselines are captured before the content ships**, or the improvement cannot be claimed. `00-07` H2-10 recorded a KPI target with no baseline behind it; that is not repeated here |
| **ME-04** | **Metric definitions come from `RP-001`.** Content does not define metrics locally (`T-06`, `CG-004`) |
| **ME-05** | **Counted, not projected** (`CP-11`, `RG-06`). Every figure carries the date it was measured |
| **ME-06** | **A metric that would not change a decision is not collected.** Every metric below names the decision it informs |
| **ME-07** | **Attribution is stated honestly.** Where content is one of several causes, the measure is reported as contributory, not causal |

---

## 2. The four measurement layers

| Layer | Question | Reported to | Cadence |
|---|---|---|---|
| **L1 — Production** | Are we producing the content on schedule and to standard? | PMO | Weekly |
| **L2 — Quality** | Is the content correct, conformant and current? | Content Lead, PMO | Per wave audit |
| **L3 — Effectiveness** | Is the content achieving what it exists to achieve? | Steering Committee | Monthly from W2 |
| **L4 — Value** | Was the investment justified? | Steering Committee, Board | Per wave gate, and at programme close |

---

## 3. L1 — Production metrics

Progress and capacity. Answers "will the content be ready for the wave gate?"

| # | Metric | Definition | Target | Decision it informs |
|---|---|---|---|---|
| **P-01** | Files approved | Count of files at `Approved` or `Published`, by enumeration | Per wave plan | Wave go/no-go |
| **P-02** | `P0` content complete for the next wave | `P0` files for wave N at `Approved` ÷ total `P0` files for wave N | **100% at gate minus 4 weeks** | Whether the wave can proceed |
| **P-03** | Schedule variance | Files approved ÷ files planned to date | ≥ 95% | Whether to add capacity or descope |
| **P-04** | Effort variance | Actual person-days ÷ estimated person-days, cumulative | Within ±20% of Master Index §7 | Re-forecast; escalate above 20% (`CG-002` §7) |
| **P-05** | Review queue depth, per gate | Files waiting, per `CG-007` gate | G1–G4 under 10; G5–G6 under 5 | Where the constraint is |
| **P-06** | Gate cycle time | Median working days from submission to gate outcome | Within `CG-007` §6 service levels | Whether to contract external review capacity |
| **P-07** | Translation throughput | Bengali files signed off per week | Per `CG-010` §9 plan | Translation capacity escalation |
| **P-08** | Rework rate | Files returned from `Review` to `Draft` ÷ files submitted | Under 15% | Whether authors need guidance or the templates need work |
| **P-09** | Escalations open | `CG-013` escalations raised and not triaged | Zero over 2 working days | Content Lead capacity |
| **P-10** | Blocked files | Files that cannot progress for a reason outside the content workstream | Reported, not targeted | What to escalate to PMO |

---

## 4. L2 — Quality metrics

Correctness and conformance. Measured at each wave audit
(`_AUDIT/AUDIT_Checklist_Recurring.md`).

| # | Metric | Definition | Target |
|---|---|---|---|
| **Q-01** | Blocking-item defects at approval | Files reaching `Approved` with an unremediated `CG-008` §5 blocking item | **Zero** |
| **Q-02** | Terminology defect rate | Sampled files containing a banned term or an unbound business object ÷ files sampled | Under 2% |
| **Q-03** | Evidence defect rate — Class A and B | Claims without a P1 source, or with a stale verification date | **Zero** |
| **Q-04** | Evidence defect rate — other classes | Sampled at 10% | Under 5% |
| **Q-05** | Broken internal links | Count | **Zero** |
| **Q-06** | Register drift | Files on disk with no register row, plus register rows claiming a file that does not exist | **Zero** |
| **Q-07** | Bilingual pairing defects | `bilingual: yes` files with no `_BN` counterpart, or at a different version | **Zero** |
| **Q-08** | In-context linguistic sign-off | Bilingual files approved without `BN-018` in-context review | **Zero** |
| **Q-09** | Accessibility content failures | WCAG 2.1 AA content-criteria failures found at release (`CG-011` §10.1) | **Zero** |
| **Q-10** | Currency | Files past their `review_due` date | Under 5%; **zero** for Class A and B |
| **Q-11** | Pin staleness | Pinned files more than one release behind (`CG-006` PN-04) | **Zero** at a wave gate |
| **Q-12** | Template conformance | Files failing the automated structural check | **Zero** |
| **Q-13** | Provisional claims | Open provisional claims (`CG-012` §6.1) | Reported; **zero** in Class A |
| **Q-14** | Cross-file contradictions | Contradictions found between files that must agree (`AUDIT_Checklist_Recurring.md` §F) | **Zero** |

---

## 5. L3 — Effectiveness metrics

**The layer that justifies the investment.** Each metric names the portal or programme KPI it
supports.

### 5.1 Help and self-service

| # | Metric | Definition | Baseline | Target | Supports |
|---|---|---|---|---|---|
| **E-01** | Self-service deflection | Status enquiries resolved without a hotline call ÷ total status enquiries | ~0 (no portal today) | **> 80%** | `P01` KPI |
| **E-02** | Help article helpfulness | "Was this helpful?" positive responses ÷ total responses | To capture at W2 | > 75% | `P01`, `HC-003` |
| **E-03** | Search-to-contact rate | Help searches followed by a support contact within 10 minutes ÷ help searches | To capture at W2 | Falling quarter on quarter | `HC-001` |
| **E-04** | Zero-result searches | Help searches returning nothing ÷ total searches | To capture at W2 | Under 5% | `HC-015` — each one is a missing article |
| **E-05** | Top unanswered questions | The 20 most frequent zero-result or escalated queries | — | Reviewed monthly; each becomes content or is closed | `HC-015`, `HC-017` |

### 5.2 UI copy and error messages

| # | Metric | Definition | Baseline | Target | Supports |
|---|---|---|---|---|---|
| **E-06** | Error-message abandonment | Sessions abandoning within 60 seconds of an error ÷ sessions encountering that error | To capture at W2 | Under 10% per message | `PS-09`, `BR-STD-04` |
| **E-07** | Error recurrence | Users hitting the same validation error twice in one session ÷ users hitting it once | To capture at W2 | Under 20% | `UI-004` — recurrence means the remedy is not clear |
| **E-08** | Booking funnel conversion | Completed bookings ÷ started bookings | Unmeasured (`P01` KPI table) | **> 72%** | `P01` primary design KPI |
| **E-09** | Step drop-off | Abandonment at each booking step | To capture at W2 | No step above 15% | `UI-037` |
| **E-10** | Form field error rate | Errors per field per 100 submissions | To capture at W1 | Falling; top 10 fields reviewed monthly | `UI-003`, `UI-004` |
| **E-11** | Language switching | Users switching from Bengali to English mid-task ÷ Bengali sessions | To capture at W2 | Under 5% | `CG-010` — switching signals the Bengali is not working |

### 5.3 Training and enablement

| # | Metric | Definition | Baseline | Target | Supports |
|---|---|---|---|---|---|
| **E-12** | Time to competence — service agent | Hours of training until assessment pass | Unmeasured | **≤ 4 hours** | `NFR-075`, `P03` KPI |
| **E-13** | Assessment pass rate, first attempt | Passes ÷ attempts | To capture at W1 | > 85% | `TR-004` |
| **E-14** | Post-training error rate | Errors per user in the first 30 days after training | To capture at W1 | Falling by cohort | `TR-002` |
| **E-15** | Job aid usage | Job aid accesses per user per week | To capture at W1 | Reported; sustained use indicates the aid is useful | `TR-022` |
| **E-16** | Certification currency | Technicians with current certification ÷ technicians requiring it | To capture at W2 | 100% | `MD-011`, `BRU-SRM-09` |

### 5.4 Operational content

| # | Metric | Definition | Baseline | Target | Supports |
|---|---|---|---|---|---|
| **E-17** | Walk-in intake time | Median minutes from greeting to service order created | To capture at W1 | **< 3 minutes** | `NFR-076`, `P03` KPI |
| **E-18** | SOP-attributed incidents | Incidents whose root cause is an SOP gap or error | To capture at W1 | Falling | `SP` category |
| **E-19** | Master data rejection rate | Transactions failing on master data validity ÷ transactions | To capture at W1 | Under 1% | `MD` category |
| **E-20** | Document rejection | Statutory or customer documents rejected or disputed on format ÷ issued | To capture at W1 | **Zero** for statutory | `DT` category |
| **E-21** | Notification opt-out | Opt-outs ÷ recipients, per message type | To capture at W2 | Under 2% | `NT-002`, `NT-003` |
| **E-22** | Notification failure | Undeliverable or failed sends ÷ sends | To capture at W2 | Under 1% | `NT-025` |

### 5.5 Localisation

| # | Metric | Definition | Baseline | Target | Supports |
|---|---|---|---|---|---|
| **E-23** | Bengali coverage per surface | Bengali strings ÷ total user-visible strings, per surface | 0 at W0 | **100%** before release | `PS-03`, `CG-010` §5 |
| **E-24** | Translation defect density | Linguistic defects found in review per 1,000 words | To capture at W1 | Under 5, falling | `BN-018` |
| **E-25** | In-production translation defects | Defects reported by users per 1,000 published strings | To capture at W2 | Under 1 | `BN-018` — the ones review missed |
| **E-26** | Truncation defects | Layout breaks caused by Bengali expansion, found at G4 or later | To capture at W1 | Zero reaching production | `BC-01`, `BN-006` |
| **E-27** | Bengali session share | Sessions in Bengali ÷ total sessions, per portal | To capture at W2 | Reported — validates the Bengali-first assumption | `PS-03` |

### 5.6 Ecosystem content

| # | Metric | Definition | Baseline | Target | Supports |
|---|---|---|---|---|---|
| **E-28** | Seller onboarding completion | Completed registrations ÷ started | Unmeasured | **> 60%** | `P07` KPI, `EO-001` |
| **E-29** | Vendor query reduction | Vendor phone and email queries, versus baseline | To capture at W3 | **−60%** | `P05` KPI, `EO-005` |
| **E-30** | Claim rejection for evidence | Brand claims rejected for incomplete evidence ÷ submitted | To capture at W4 | Falling; supports **> 92%** approval | `P08` KPI, `EO-004` |
| **E-31** | Corporate portal adoption | Contracted clients actively using `P04` ÷ contracted clients | Unmeasured | **> 85%** | `P04` KPI, `EO-007` |

---

## 6. L4 — Value metrics

Reported at each wave gate and at programme close.

| # | Metric | Definition | Purpose |
|---|---|---|---|
| **V-01** | Cost per content file | Total content effort ÷ files approved | Benchmarks the estimate in Master Index §7 and improves the next forecast |
| **V-02** | Support cost avoided | (Baseline contacts − actual contacts) × cost per contact | The largest single quantifiable content return |
| **V-03** | Training cost avoided | (Baseline training hours − actual hours) × loaded hourly cost × users trained | `NFR-075` is a content-delivered target |
| **V-04** | Rework cost avoided | Reduction in operational rework attributable to clearer SOPs and knowledge | Contributory, reported honestly (`ME-07`) |
| **V-05** | Compliance exposure avoided | Statutory documents issued correctly; filings accepted first time | Reported as risk avoided, not as currency |
| **V-06** | Adoption contribution | Portal adoption against target, where content was a named intervention | Contributory |
| **V-07** | Content debt | Files past review date + open provisional claims + open waivers + unremediated audit findings | The liability the programme carries forward |

> **`V-07` is the honest counterweight.** Every other value metric shows what content delivered.
> Content debt shows what it deferred. Both go to the Steering Committee together.

---

## 7. Instrumentation

Metrics need data. Most of it does not exist yet and must be requested **before** the surface is
built, not after.

| Metric group | Data source | Required by | Owner |
|---|---|---|---|
| Production (L1) | The content repository, register and gate queue | W0 | Programme Content Lead |
| Quality (L2) | Automated checks + wave audits | W0 | Content Lead + Platform |
| Help and search (E-01…E-05) | Help platform analytics; support ticket categorisation | W2 | Support + BI |
| UI and funnel (E-06…E-11) | Portal instrumentation feeding `M25` — required by `PS-10` | W1 | Platform + BI |
| Training (E-12…E-16) | LMS (`M22`) | W1 | L&D |
| Operational (E-17…E-22) | The ERP itself | W1 | BI |
| Localisation (E-23…E-27) | i18n tooling, translation memory, portal analytics | W1 | Localisation + Platform |
| Ecosystem (E-28…E-31) | Portal analytics and the relevant modules | W3–W4 | BI |

| # | Rule |
|---|---|
| **IN-01** | `PS-10` requires analytics instrumentation on every critical funnel, feeding `M25`. **Content metrics are specified as part of that instrumentation**, not requested afterwards |
| **IN-02** | Error-message instrumentation must record **which message** was shown, not only that an error occurred. Without the message ID, `E-06` and `E-07` cannot be computed |
| **IN-03** | Help analytics must record the **search string** on zero-result searches (`E-04`, `E-05`) |
| **IN-04** | Language and language-switch events must be recorded (`E-11`, `E-27`) |
| **IN-05** | A metric with no instrumentation is not reported as zero. It is reported as **not instrumented** |

> **`IN-02` is the one most likely to be missed.** Generic error logging cannot distinguish a
> message that works from one that does not, and error-message quality is the single most direct
> content contribution to `PS-09` and `BR-STD-04`.

---

## 8. Baselines

`ME-03`. Baselines are captured **before** content ships, or improvement cannot be claimed.

| Baseline | Capture method | Capture by | Status |
|---|---|---|---|
| Hotline contact volume and mix | Current contact-centre records | W0 | **To capture** |
| Current time to competence per role | Observation and HR records | W0 | **To capture** |
| Current walk-in intake time | Timed observation at a sample of branches | W0 | **To capture** |
| Current vendor query volume | Procurement inbox and call records | W1 | **To capture** |
| Current document dispute and rejection rate | Finance and Ops records | W0 | **To capture** |
| Current rework rate | Existing service records | W0 | Partially available |
| Current Bengali/English preference | Survey plus website analytics | W1 | **To capture** |
| Booking funnel conversion | **None — no portal exists.** Recorded as "unmeasured" in `P01` KPIs | — | Not applicable |

> **Where no baseline exists, say so.** `P01` already records "unmeasured" against booking funnel
> conversion. That is the correct treatment — better than inventing a number to improve on, which
> is the failure `00-07` H2-10 recorded.

---

## 9. Reporting

| Report | Audience | Cadence | Contents |
|---|---|---|---|
| Content status | PMO | Weekly | L1 production, queue depths, blockers, escalations |
| Content quality | Content Lead | Per wave audit | L2, with the audit findings |
| Content effectiveness | Steering Committee | Monthly from W2 | L3 against target, with commentary |
| Content value | Steering Committee | Per wave gate | L4, including content debt (`V-07`) |
| Programme close | Board | At close | L4 cumulative, cost per file, benefits realised |

| # | Rule |
|---|---|
| **RP-01** | Every reported figure carries the date it was measured (`ME-05`) |
| **RP-02** | A metric with no baseline is reported as **absolute with no comparison**, never as an improvement |
| **RP-03** | Contributory metrics are labelled contributory (`ME-07`) |
| **RP-04** | Content debt is reported at every wave gate alongside the positive metrics |
| **RP-05** | Metric definitions come from `RP-001`; this file cites them and does not restate them |

---

## 10. Review

| Activity | Cadence | Owner |
|---|---|---|
| Are the metrics still the right ones? | Every two waves | Content Lead |
| Retire metrics that have not changed a decision (`ME-06`) | Every two waves | Content Lead |
| Add metrics for content types entering production | Per wave | Content Lead |
| Verify instrumentation against `IN-01`–`IN-05` | Before each portal release | Content Lead + Platform |
| Recalibrate targets against actuals | Per wave gate | Content Lead + BI |

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`CG-002_Content_Operating_Model_and_RACI.md`](CG-002_Content_Operating_Model_and_RACI.md) | §9 capacity and the funding gap these metrics defend |
| [`CG-008_Content_Definition_of_Done_and_QA_Checklist.md`](CG-008_Content_Definition_of_Done_and_QA_Checklist.md) | The quality gates L2 measures |
| [`CG-011_Accessibility_Content_Standard.md`](CG-011_Accessibility_Content_Standard.md) | §10.1 targets feeding `Q-09` |
| [`CG-012_Content_Sourcing_and_Evidence_Rules.md`](CG-012_Content_Sourcing_and_Evidence_Rules.md) | Evidence defect rates feeding `Q-03`, `Q-04` |
| [`CG-013_Content_Risk_and_Legal_Escalation_Rules.md`](CG-013_Content_Risk_and_Legal_Escalation_Rules.md) | Escalations feeding `P-09` |
| `RP-001` KPI Dictionary and Metric Definition Standard | Where every metric definition lives (`ME-04`) |
| `RP-015` Benefits Realisation and KPI Baseline Register | Where the §8 baselines are recorded |
| `_AUDIT/AUDIT_Checklist_Recurring.md` | How L2 is measured |
| `06-02` KPI, Benefits & Acceptance Criteria | The programme KPIs content metrics map to |
| `04-00` §P01–P12 KPI tables | The portal KPIs content contributes to |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Four measurement layers, 10 production, 14 quality, 31 effectiveness and 7 value metrics, instrumentation requirements tied to `PS-10`, baseline capture plan with honest treatment of missing baselines, reporting cadence including content debt | Programme Content Lead (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] Every metric maps to a programme or portal KPI, or names the decision it informs
- [x] Baselines identified, with "no baseline exists" stated where true rather than invented
- [x] Instrumentation requirements stated as build requirements tied to `PS-10`, not as afterthoughts
- [x] Content debt included as a reported measure alongside positive metrics
- [x] Metric definitions deferred to `RP-001` rather than restated (`CP-01`)
- [x] All internal links resolve
- [x] Bengali counterpart — n/a
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
