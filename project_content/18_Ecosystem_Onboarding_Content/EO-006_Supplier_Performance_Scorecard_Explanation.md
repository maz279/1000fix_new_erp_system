---
id: EO-006
title: Supplier Performance Scorecard Explanation
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Procurement
author: Procurement Manager with Quality and Content Design
reviewers: [Supply Chain Director, Quality Manager, Finance Manager, Warehouse Manager, Master Data Owner, BI Lead, Content Design Lead]
approver: Content Design Lead with Procurement Manager
content_class: D
purpose: >
  What each metric on a supplier's scorecard measures, where the number comes from, what the band
  means, and the specific actions that move each metric. A scorecard a supplier does not
  understand is a scorecard they dispute rather than respond to — and because the lowest band for
  two consecutive periods triggers mandatory corrective action and a third triggers suspension
  review, a misunderstood scorecard becomes a commercial dispute about supply continuity rather
  than a conversation about delivery performance.
traces_to: [P05, M42, M16, M41, M15, M20, M23, 04-00 P05, 05-04 §8 EA-01, EA-02, EA-06, FR-SRM2-003, FR-SRM2-027, FR-SRM2-028, FR-SRM2-029, FR-SRM2-030, FR-SRM2-031, FR-SRM2-032, FR-SRM2-033, FR-SRM2-034, BRU-SRM2-08, BRU-SRM2-09, BRU-SRM2-10, BRU-SRM2-11, BRU-SRM2-13, BRU-SRM2-18, BRU-SRM2-19, BRU-SRM2-20, KPI-048, KPI-049, KPI-043, MD-016, MD-022, MD-026, MD-038, LG-006, SP-017, SP-018, SP-029, UI-015, HC-007, NT-011, RP-001, RP-005, EO-005, EO-011, EO-014]
priority: P3
wave: W3
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M42_Supplier_Relationship_and_Performance.md §5.5 FR-SRM2-027 scorecard computed from M16 and M41 transaction facts — on-time delivery, delivery-in-full, quality rejection rate, lead-time reliability, price adherence, invoice accuracy, documentation completeness and responsiveness (BR-SCM-007); FR-SRM2-028 weighted model per category and risk tier with a banded rating and trend; FR-SRM2-029 supplier-facing scorecard on P05 showing metrics, underlying data and trend; FR-SRM2-030 review cycle; FR-SRM2-031 corrective action to verified closure; FR-SRM2-032 development plans
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M42_Supplier_Relationship_and_Performance.md §9 BRU-SRM2-08 performance facts originate in M16 and M41 and are not editable within M42; BRU-SRM2-09 a published scorecard is immutable and a correction is a re-publication with a stated reason; BRU-SRM2-10 lowest band for two consecutive periods enters mandatory corrective action, a third triggers suspension review; BRU-SRM2-11 overdue corrective action escalates; BRU-SRM2-18 review cadence by segment
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M42_Supplier_Relationship_and_Performance.md §15 — KPI-048 is the only canonical identifier in 06-02 §2.6 touching M42 and is assigned there to M16; fourteen further metrics are unregistered and require KPI-0nn allocation, recorded as an audit action
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P05 Performance capability "view own scorecard — on-time delivery, quality, responsiveness — with detail"
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §2.6 KPI-048 vendor on-time delivery unmeasured baseline, 88% at W4, 92% at W8; KPI-049 three-way match exception rate; KPI-043 part availability at first request
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Supplier Performance Scorecard Explanation

| Item | Value |
|---|---|
| Audience | Suppliers who receive a scorecard, and the 1000FiX people who publish and discuss it |
| Population | 200–500 supplier portal users (`04-00` P05) |
| Portal | `P05` Performance section (`FR-SRM2-029`) |
| Language | **English only** (`CG-010` §3.2) |
| Wave | W3 · Months 9–13 — **but `M42`, which computes the scorecard, is W4** (`O-01`) |
| Consequence attached | Lowest band **twice** → mandatory corrective action · **three times** → suspension review (`BRU-SRM2-10`) |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3), all
> six sections in order. The three `EO` additions are applied to the scorecard cycle rather than
> to an admission process: §4.1 is the **journey** a period travels from transaction to review,
> §4.5 is the **checklist** a supplier uses to keep their own score accurate, and §4.7 is the
> **first 90 days** — the three publications in which a supplier decides whether to trust it.
> Declared because `CG-009` §3 does not anticipate the adaptation and template 15 does not exist.

---

## 1. Purpose

The Master Index states this file's justification in one line: *"a scorecard a supplier does not
understand is a scorecard they dispute rather than respond to."*

That is not a customer-service observation. `BRU-SRM2-10` attaches a real commercial consequence:

> A supplier scoring in the **lowest band for two consecutive periods enters mandatory corrective
> action**; a **third** consecutive period triggers **suspension review**.

A supplier facing suspension will contest the measurement, and they will contest it at the point
where it is hardest to answer — after three periods have already been published, when
`BRU-SRM2-09` has made all three immutable. The only defence is that the supplier understood
every metric from the first publication and had a stated way to move each one.

**The pack is therefore built around one question per metric: *what did the supplier do, or fail
to do, that moved this number?*** A metric with no answer to that question does not belong on a
supplier-facing scorecard, however useful it is internally.

---

## 2. Scope

**In scope.** Each metric's definition, source, grain and period; the weighting model and why it
differs by category and risk tier; the bands and what each triggers; the trend view; what a
supplier can do to move each metric; the corrective-action and development-plan processes; the
review cadence by segment; the dispute route and its limits; and the data-quality obligations
that fall on the supplier rather than on us.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| Registration, qualification, activation and the transaction cycle | **`EO-005`** |
| Portal terms and the Supplier Code of Conduct | `LG-006` |
| **Metric formulae, numerators, denominators and certified definitions** | **`RP-001`** KPI Dictionary and Metric Definition Standard |
| Weight values and band thresholds as configuration | `M42` `FR-SRM2-028`; **unconfigured**, `O-03` |
| The internal procure-to-pay and receipt procedures that create the facts | `SP-017`, `SP-018` |
| Quality nonconformity and CAPA where a rejection becomes one | `M23`, `SP-029` |
| Rejection reason-code values | `MD-026` |
| Price change governance | `EO-005` §4.6; communication `EO-011` |
| Suspension, blocking and exit | **`EO-014`** |
| Screens, help and notifications | `UI-015`, `HC-007`, `NT-011` |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Supplier's commercial owner** | Understanding the band, the trend and what is at stake |
| **Supplier's operations / dispatch lead** | The delivery metrics and the actions that move them |
| **Supplier's finance contact** | Invoice accuracy and documentation completeness |
| **1000FiX Procurement Officer** | The explanation given at a review meeting, so it is the same explanation every time |
| **Category owner** | Why the weighting differs for their category |
| **Quality Manager (`R32`)** | Where a quality metric becomes a corrective action or a nonconformity |
| **Supply Chain Director** | Concentration and single-source consequences (`FR-SRM2-033`) |

---

## 4. Content

### 4.1 The scorecard cycle

| # | Stage | What happens | Who | Rule |
|---|---|---|---|---|
| **1** | **Transact** | Orders, receipts, inspections, invoices and payments occur | Both parties | — |
| **2** | **Fact capture** | Every metric's raw fact is created **in `M16` and `M41` at the moment of the transaction** | System | `BRU-SRM2-08` — **facts are not editable in `M42`** |
| **3** | **Compute** | The weighted composite and band are computed for the period, per category and risk tier | System | `FR-SRM2-027`, `FR-SRM2-028` |
| **4** | **Publish** | The scorecard is published to `P05` with metrics, underlying data and trend | System | `FR-SRM2-029`; **`BRU-SRM2-09` — published is immutable** |
| **5** | **Review** | Meeting at the segment cadence, agenda generated from the scorecard, outcome minuted | Procurement + supplier | `FR-SRM2-030`, `BRU-SRM2-18` |
| **6** | **Act** | Corrective action where required; development plan for strategic and critical suppliers | Both parties | `FR-SRM2-031`, `FR-SRM2-032` |
| **7** | **Verify** | Corrective action tracked to **verified closure**; overdue actions escalate | Quality / Procurement | `BRU-SRM2-11` |
| **8** | **Re-measure** | The next period, on the same definitions | System | — |

**Stage 2 is the sentence that makes the whole scorecard defensible.** No 1000FiX person can
change a performance fact after the event. A correction is not an edit — `BRU-SRM2-09` requires
a **re-publication with a stated reason**, which leaves both versions in the record.

### 4.2 The metrics

Eight metrics from `FR-SRM2-027`. For each: what it counts, where the fact comes from, and the
**one action** that moves it most.

| # | Metric | What it counts | Fact created at | What moves it |
|---|---|---|---|---|
| **1** | **On-time delivery** | Deliveries arriving on or before the **confirmed** date | `M16` PO confirmation → `M41` receipt | **Confirm a date you will meet, not the one requested.** A confirmed date is the commitment; the requested date is not measured |
| **2** | **Delivery in full** | Order lines delivered complete against the confirmed quantity | `M41` receipt | Tell us about a short supply **before** dispatch; a notified short delivery and an unnotified one are not the same event |
| **3** | **Quality rejection rate** | Lines rejected at inspection, as a share of lines received | `M41` / `SP-018` inspection | Address the reason code (`MD-026`), not the rejection. Repeat reasons are what trigger corrective action |
| **4** | **Lead-time reliability** | Actual lead time against quoted, within the tolerance for the category | `M16` order → `M41` receipt | Quote a real lead time. A short quoted lead time missed scores worse than a long one met |
| **5** | **Price adherence** | Invoiced price against the agreed price list on the order date | `M16` PO ↔ `M20` invoice | Submit price changes through `FR-SRM2-023` governance **before** invoicing. `BRU-SRM2-14` blocks the order anyway; the metric records the attempt |
| **6** | **Invoice accuracy** | Invoices matching without exception in the three-way match | `M20` matching | Invoice against the PO, at the PO price, for the received quantity. `KPI-049` tracks the exception rate from our side |
| **7** | **Documentation completeness** | Required documents present and current at transaction time | `M42` document register, `M16` | Renew before expiry. `BRU-SRM2-04` suspends automatically on lapse — the metric records it before the suspension does |
| **8** | **Responsiveness** | RFQ response, PO acknowledgement and query turnaround within the stated windows | `P05` events | Acknowledge in the portal. **This is the one metric fully in the supplier's control and it is the one most often ignored** |

> **`04-00` P05 describes the supplier-facing scorecard as "on-time delivery, quality,
> responsiveness".** `FR-SRM2-027` computes eight. **All eight are shown**, because a supplier
> shown three of the eight metrics that determine their band cannot act on the other five. The
> three named in `04-00` are the headline; the eight are the scorecard.

### 4.3 Weighting, bands and trend

**Weighting differs by category and risk tier, deliberately.** `FR-SRM2-028` configures the
weights per category and tier, and the reason is stated to suppliers so it does not read as
favouritism:

| Category shape | What weighs most | Why |
|---|---|---|
| Critical spare parts | Quality rejection rate; on-time delivery | A defective or late critical part stops a repair and breaches an SLA (`KPI-043`) |
| High-volume consumables | Delivery in full; invoice accuracy | Volume makes small exception rates expensive to administer |
| Logistics services | On-time delivery; responsiveness | The service *is* timeliness |
| Recycling and disposal | Documentation completeness | The certificate is the compliance artefact |
| Low-risk transactional | Invoice accuracy; responsiveness | Little else is materially at risk |

**Bands.** `FR-SRM2-028` produces a banded overall rating with a trend across periods. Each band
carries a stated consequence:

| Band | Consequence | Rule |
|---|---|---|
| Top | Eligible for strategic or preferred segmentation; considered first in sourcing | `FR-SRM2-003` |
| Middle | Steady state; reviewed at the segment cadence | `BRU-SRM2-18` |
| Watch | Discussed at review with a named improvement expectation | `FR-SRM2-030` |
| **Lowest** | **First period:** discussed · **Second consecutive:** mandatory corrective action · **Third consecutive:** suspension review | **`BRU-SRM2-10`** |

**The band values themselves are unconfigured** — `O-03`. This file states the mechanism and the
consequence ladder; the numbers are `M42` configuration and the pack does not estimate them.

**Trend matters more than level for a new supplier.** A supplier three months into a relationship
has a level built from few transactions and a trend built from three points. §4.7 handles the
cold start.

### 4.4 Review cadence

`BRU-SRM2-18` sets it by segment, not by score:

| Segment | Cadence | Agenda |
|---|---|---|
| Strategic | **Quarterly** | Generated from the scorecard (`FR-SRM2-030`); development plan progress (`FR-SRM2-032`) |
| Preferred | **Half-yearly** | Scorecard, open corrective actions, price and agreement position |
| Approved | **Annually** | Scorecard and re-qualification currency |
| Transactional | **On exception** | Triggered by band or by a corrective action |

**Outcomes are minuted.** A review whose outcome is not recorded cannot be relied on at the third
period, which is when `BRU-SRM2-10` bites.

### 4.5 The supplier's data-quality checklist

Most scorecard disputes are data disputes, and most data disputes have a supplier-side cause that
the supplier could have prevented. This checklist is the pack's most practical content.

| # | Check | Why it protects the supplier | Frequency |
|---|---|---|---|
| 1 | **Confirm every PO date in the portal** — do not accept silently | An unconfirmed PO is measured against the **requested** date, which the supplier never agreed to | Per order |
| 2 | Acknowledge POs in the portal, not by email | Email acknowledgement creates no event; metric 8 records nothing | Per order |
| 3 | Submit an ASN for every dispatch | Separates a transit delay from a dispatch delay | Per dispatch |
| 4 | Notify short supply **before** dispatch | Converts an unexplained short delivery into a managed one | As it arises |
| 5 | Invoice against the PO, at the PO price, for the received quantity | Prevents match exceptions that score against metric 6 | Per invoice |
| 6 | Check the receipt and inspection outcome in the portal | An unchallenged rejection stands and scores | Weekly |
| 7 | **Renew documents before expiry** — the portal shows the dates | Prevents both a metric-7 hit and an automatic suspension (`BRU-SRM2-04`) | Monthly |
| 8 | Keep contact details current | An unanswered query scores as unresponsive whoever it was sent to | Quarterly |
| 9 | Route price changes through the governance route | Metric 5; `BRU-SRM2-14` blocks the order regardless | As it arises |
| 10 | **Read the scorecard when it is published** | `BRU-SRM2-09` makes it immutable; the time to query a fact is at publication, not at suspension review | Per period |

### 4.6 Disputing a scorecard — what can and cannot be changed

| Claim | Route | Outcome |
|---|---|---|
| "The underlying fact is wrong" | Raise with Procurement, with the transaction reference | If the `M16`/`M41` fact is wrong, it is corrected at source and the scorecard is **re-published with a stated reason** (`BRU-SRM2-09`) |
| "The delay was caused by 1000FiX" | Raise at the review with evidence | Recorded; where the cause is ours, the fact is annotated. **The metric definition is not varied for one supplier** |
| "The weighting is unfair for my category" | Category owner | A weighting change is a `FR-SRM2-028` configuration decision affecting **every supplier in the category**, and is never made for one |
| "The band threshold is too harsh" | Procurement Manager | A policy route, not a dispute route |
| "I did not know this was measured" | — | **This file exists so that claim cannot be made.** Its issue date and version are recorded against the supplier |

> **What a published scorecard is not.** It is not editable, not negotiable per supplier, and not
> a substitute for the corrective-action process. A supplier who disputes rather than acts on two
> consecutive lowest-band periods arrives at the third with the same score and a weaker position.

### 4.7 The first 90 days — the first three scorecards

| Publication | What it can and cannot show | What the review should focus on |
|---|---|---|
| **First** | A level built from few transactions; **no meaningful trend** | Whether the supplier can read it, and whether every metric's fact is recognisable to them |
| **Second** | A two-point trend; metric 8 responsiveness is already fully valid | The first metric that has moved, and why |
| **Third** | A usable trend; **`BRU-SRM2-10`'s two-period clock has now run once** | Whether a corrective action is required — and if so, the supplier has already had two publications' notice |

**The cold-start protection is the corrective-action process itself, not a scoring rule.**
`BRU-SRM2-10` requires two *consecutive* lowest-band periods before mandatory corrective action
and three before suspension review, which builds in the time for a new supplier to learn the
measurement. The pack states this explicitly, because a new supplier's first low band otherwise
reads as a threat.

**One protection is missing and is stated as such.** Nothing defines a **minimum transaction
count** below which a period is not scored. A supplier with two deliveries in a period can be
placed in the lowest band by one late delivery. Recorded as `O-04`.

### 4.8 Rules

| # | Rule |
|---|---|
| **SD-01** | Every metric shown to a supplier states **what it counts, where the fact is created, and one action that moves it**. A metric failing this test is internal-only |
| **SD-02** | All eight `FR-SRM2-027` metrics are shown, not the three headline metrics from `04-00` |
| **SD-03** | The pack never states a weight value or a band threshold. `M42` configuration holds them; `RP-001` will hold the certified definitions |
| **SD-04** | The consequence ladder (`BRU-SRM2-10`) is stated **at the first publication**, not at the second |
| **SD-05** | Facts are described as originating in `M16` and `M41` and being uneditable in `M42` (`BRU-SRM2-08`), because that is what makes the score defensible |
| **SD-06** | A correction is described as a **re-publication with a stated reason**, never as an edit (`BRU-SRM2-09`) |
| **SD-07** | Weighting differences by category and tier are explained, not merely applied |
| **SD-08** | A supplier sees only their own scorecard; never another's, never the ranking, never 1000FiX cost or margin (`EA-01`, `EA-02`, `EA-06`, `BRU-SRM2-20`) |
| **SD-09** | The dispute route distinguishes a **wrong fact** (correctable) from a **disliked definition** (not correctable per supplier) |
| **SD-10** | Corrective action is tracked to **verified** closure, and overdue actions escalate (`FR-SRM2-031`, `BRU-SRM2-11`). "Closed" without verification is not closed |
| **SD-11** | Where a supplier is the single qualified source for a critical part, the pack states that suspension review carries a continuity assessment (`BRU-SRM2-13`) — **the supplier is entitled to know that the decision is not purely mechanical** |
| **SD-12** | The pack is issued **before** a supplier's first scorecard, and its issue is recorded against the supplier |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`EO-005`](EO-005_Vendor_and_Supplier_Onboarding_Pack.md) | Registration, qualification and the transaction cycle that creates every fact |
| `M42` §5.5 | The scorecard, the model, the review cycle, corrective action and development plans |
| `M16`, `M41` | Where every performance fact originates (`BRU-SRM2-08`) |
| [`SP-017`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-017_SOP_Procurement_to_Payment.md), [`SP-018`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md) | The procedures that create the receipt and inspection facts |
| [`MD-026`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md) | Rejection reason codes behind metric 3 |
| [`MD-016`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md) | Segment, risk tier and document expiry dates behind metric 7 |
| `M23`, [`SP-029`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) | Where a quality metric becomes a nonconformity |
| **`RP-001`** | The certified metric definitions this file describes in prose. **Written** — the read-across in `O-02` has not been done |
| [`RP-005`](../14_Reporting_Analytics_and_KPI/RP-005_Dashboard_Specification_Pack_External_Audiences.md) | Dashboard specification for external audiences — the surface the supplier's own scorecard is rendered on, with the `EA-*` scoping this file's §4.7 relies on |
| [`LG-006`](../10_Legal_Policy_and_Compliance/LG-006_Vendor_Portal_Terms_and_Supplier_Code_of_Conduct.md) | The contractual basis for performance obligations and consequences |
| [`UI-015`](../03_UI_Copy_and_Microcopy/03B_Portals/UI-015_P05_Vendor_and_Supplier_Portal_UI_Copy_Pack.md), [`HC-007`](../09_Help_Centre_and_Self_Service/09A_Help_Sets_By_Portal/HC-007_Help_Set_P05_Vendor_and_Supplier_Portal.md), [`NT-011`](../04_Notification_and_Messaging/04C_Email/NT-011_Email_Template_Library_Vendor_and_Supplier.md) | The portal view, help and publication notice |
| [`EO-011`](EO-011_Rate_Card_and_Pricing_Communication_Pack.md), [`EO-014`](EO-014_Ecosystem_Offboarding_and_Exit_Content.md) | Price change communication; suspension and exit |

> **Rule-citation attribution.** **BRU-SRM2-\***  → `M42` §9 — these are **module-scoped** rule families and **`05-05` carries none of them**. Stated per `AUDIT-015` R-11, which asked that the convention be recorded once rather than rediscovered by each extraction.

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Annually, and whenever a weight or band is reconfigured |
| Trigger for out-of-cycle review | A change to `FR-SRM2-027` metrics or `FR-SRM2-028` weights; a band threshold change; a dispute revealing an unexplained metric; `RP-001` publishing certified definitions; a change to `BRU-SRM2-10`'s consequence ladder |
| Owner | Procurement Manager, with the Quality Manager for metric 3 and the Finance Manager for metrics 5 and 6 |
| Change control | **A change to a metric definition, weight or band applies from the next period, never to a published one** (`BRU-SRM2-09`), and is notified to suppliers before that period begins |
| Effectiveness measure | Scorecard disputes as a share of publications, and the share of corrective actions closed to verified closure on time — a high dispute rate means the explanation failed, not that suppliers are difficult |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **This file is registered W3 and `M42`, which computes the scorecard, is W4** (`02-02` §wave). `P05` is W3, so the portal section exists a wave before anything can populate it. **An explanation of a scorecard that cannot yet be produced is the sharpest form of the sequencing defect** — `EO-005` `O-01` records the same gap one level less acutely, and `06-01` §3 lists `M42` in no wave at all | Programme Content Lead with Supply Chain Director | **W3 — register sequencing decision** |
| **O-02** | **`RP-001` now exists and none of these eight metrics has been read across against it.** `AUDIT-014` TS-12 recorded `RP-001` as *"blocked-on by five files across four categories"* and unwritten; **it was authored 2026-08-18 and the register does not record it** — see `AUDIT-015` EO-01. `RP-001`'s own purpose states that *"one hundred and twenty-three citations across sixty-eight written content files already point at this file"*. **The dependency has therefore changed shape rather than closed**: the definitions exist, and §4.2's eight prose descriptions have not been reconciled to them. Until they are, "on-time" may mean one thing here and another in the dictionary, and §4.6's dispute route would point at two authorities | BI Lead with Procurement Manager | **W3 — before the first publication** |
| **O-03** | **No weights, bands or thresholds exist.** `FR-SRM2-028` configures them per category and risk tier; nothing in the repository holds a value. §4.3 therefore states a mechanism and a consequence ladder with **no numbers**, and `BRU-SRM2-10`'s "lowest band" has no definition | Procurement Manager with Supply Chain Director | **W4 — before the first scorecard is computed** |
| **O-04** | **No minimum transaction count protects a low-volume supplier.** §4.7 records the exposure: a supplier with two deliveries can reach the lowest band on one late delivery, and two such periods trigger mandatory corrective action under `BRU-SRM2-10`. **`M42` has no equivalent of a statistical-significance floor**, and `EO-002` `O-01` records the identical gap on the marketplace side — **one design question, two ecosystems** | Procurement Manager with BI Lead | **W4 — before the first publication** |
| **O-05** | **Fourteen of the fifteen metrics `M42` §15 lists are unregistered.** `M42` §15 states it plainly: `KPI-048` is the only canonical identifier in `06-02` §2.6 touching `M42`, and it is **assigned there to `M16`** while `_CATEGORY_OVERVIEW.md` §7 assigns it to `M42`. **The metric this pack's headline is built on has a contested owner and no other metric has an identifier at all.** `M42` §15 already calls this an audit action. **This is an instance of `AUDIT-015` RP-01, not a new finding**: that audit counted **250 KPI identifiers in use against 95 registered in `06-02`**, with 196 unregistered, and recommended widening the register per `RP-001` §4.3 (R-01). The portal targets below are part of the 196. | Enterprise Architecture with BI Lead | **W3** |
| **O-06** | **No review-meeting content exists.** `FR-SRM2-030` generates an agenda from the scorecard and requires minuted outcomes across four cadences and 200–500 suppliers. **No `SP` procedure covers the supplier performance review** — `SP-017` is procure-to-pay and stops at payment — and no `DT` template holds the minute. §4.4's "outcomes are minuted" currently has nothing to minute onto | Business Process Analysts with Procurement Manager | **W4 — before the first strategic quarterly review** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the `EO` additions applied to the scorecard cycle and the adaptation declared
- [x] **The `BRU-SRM2-10` consequence ladder stated up front as the reason the file exists**
- [x] Eight-stage cycle, with the uneditable-fact rule identified as what makes the score defensible
- [x] All eight `FR-SRM2-027` metrics explained — **not the three named in `04-00`** — each with its fact source and one action that moves it
- [x] Weighting differences explained by category shape rather than asserted
- [x] Bands stated with their consequences, and the missing values marked rather than estimated
- [x] Review cadence by segment, with minuted outcomes
- [x] **Ten-point supplier data-quality checklist — the pack's most actionable content**
- [x] Dispute route distinguishing a wrong fact from a disliked definition
- [x] First-90-days section covering the cold start and naming the missing volume floor
- [x] Twelve rules, including the single-source continuity statement
- [x] All internal links resolve
- [x] Six open items recorded
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` file is W3, `M42` is W4 — outstanding; the scorecard cannot yet be produced**
- [ ] **`O-02` `RP-001` exists and the eight metrics have not been read across against it — outstanding**
- [ ] **`O-03` no weights, bands or thresholds — outstanding; §4.3 has a ladder and no numbers**
- [ ] **`O-04` no minimum transaction count — outstanding; a two-delivery supplier can reach corrective action**
- [ ] **`O-05` fourteen metrics unregistered and `KPI-048`'s owner contested — outstanding**
- [ ] **`O-06` no review procedure or minute template — outstanding**
- [ ] Named approver recorded — **pending Content Design Lead with Procurement Manager**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
