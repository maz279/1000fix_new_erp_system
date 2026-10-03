---
id: EO-013
title: Ecosystem Dispute Resolution Content
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Marketplace Operations with Legal
author: Marketplace Operations with Legal Counsel and Content Design
reviewers: [Chief Commercial Officer, Chief Financial Officer, Legal Counsel, Quality Manager, Data Protection Officer, Procurement Manager, Partnerships, Localisation Lead, Content Design Lead]
approver: Content Design Lead with Legal Counsel
content_class: D
purpose: >
  How a dispute is raised, what evidence is required, how long each stage takes, who decides, what
  remedies are available and how a decision is appealed — for marketplace sellers, suppliers and
  referral, alliance and channel partners. Payouts are blocked entirely while a dispute is open,
  so every day the process takes is a day a counterparty is unpaid; the dispute rate target is
  below 1.5% and Gate 7 requires every dispute resolved within SLA. A process that is not written
  down is a process that runs at the speed of whoever is least busy, and the party waiting for
  money experiences that as a decision against them.
traces_to: [P07, P05, P12, M12, M40, M42, M20, M23, M24, M53, M34, 04-00 P07, 05-04 §6 SOD-06, SOD-60, FR-MKP-055, FR-MKP-058, FR-MKP-059, FR-MKP-060, FR-MKP-061, FR-MKP-062, FR-MKP-063, FR-MKP-064, FR-MKP-065, FR-MKP-066, FR-SRM2-031, FR-PCM-024, FR-PCM-027, FR-PCM-029, BRU-ECM-09, BRU-MKP-05, BRU-MKP-17, BRU-MKP-18, BRU-MKP-20, BRU-BIL-03, BRU-BIL-04, BRU-SRM2-09, BRU-PCM-05, BRU-PCM-09, AUT-MKP-11, AUT-MKP-12, KPI-081, KPI-C12-03, G7-04, MD-026, LG-003, LG-004, LG-005, LG-006, LG-007, SP-004, SP-005, SP-024, SP-028, UI-017, UI-034, HC-009, NT-012, DT-039, DT-040, RF-006, EO-001, EO-002, EO-005, EO-006, EO-009, EO-011, EO-014]
priority: P2
wave: W7
bilingual: yes
bn_counterpart: EO-013_Ecosystem_Dispute_Resolution_Content_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M12_Marketplace_and_Seller_Ecosystem.md §5.6 FR-MKP-058…063 dispute intake with category, evidence and desired remedy; workflow through triage, evidence exchange, mediation, decision and remedy with SLA at each stage; payout hold on dispute; remedy execution instructing M20 and M01; 1000FiX-first remediation; seller recovery within declared limits with notice and appeal; §8.3 dispute lifecycle; §11 AUT-MKP-11 atomic blocking on raise, AUT-MKP-12 remedy execution on decision
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md §8 BRU-ECM-09 — disputes are decided by 1000FiX, not by the parties; the decision and its evidence are recorded
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §2.9 KPI-081 marketplace dispute rate < 1.5% by W8; §4 Gate 7 G7-04 "dispute rate below target with all disputes resolved within SLA"
    verified: 2026-08-18
    class: P1
  - source: project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-024_SOP_Marketplace_Seller_Onboarding_and_Governance.md §5.5 steps 22–27, §6, §11 — 1000FiX decides, not the parties; an operator who imposed a consequence may not decide the appeal (SOD-60), stated as having no compensating control; payout blocked entirely while a dispute is open
    verified: 2026-08-18
    class: P1
  - source: Digital Commerce Operation Guidelines 2021 (Ministry of Commerce, Bangladesh) — the e-commerce entity is responsible for dealing with complaints against itself in the first instance and resolving them within 72 hours; a compliance officer must be appointed to coordinate with the Directorate of National Consumer Rights Protection; the marketplace owner must finalise payment to the business owner within ten days after deducting charges and commission
    verified: 2026-08-18
    class: P2
  - source: Consumers' Right Protection Act 2009 (Bangladesh) §60 — a complaint must be made to the Director General or an officer of the Directorate within 30 days of the cause of action arising, in writing, with the receipt for the products or services annexed; complaints may be made in person, by fax, email, website or other electronic means
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# Ecosystem Dispute Resolution Content

| Item | Value |
|---|---|
| Audience | Marketplace sellers · suppliers · referral, alliance and channel partners — and the operators who decide |
| Portals | `P07`, `P05`, `P12` for the parties; `UI-034` Marketplace Console for the operator |
| Language | **Bilingual** — a seller cannot use a process they cannot read |
| Wave | W7 · Months 27–30 |
| Money at stake | **Payout is blocked entirely while a dispute is open** (`BRU-BIL-03`, `BRU-MKP-05`, `SLC-04`) |
| Targets | `KPI-081` dispute rate **< 1.5%** · `G7-04` **all disputes resolved within SLA** |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3), all
> six sections in order. The three `EO` additions are applied to the dispute rather than to a
> counterparty: §4.2 is the **journey** a dispute travels, §4.4 is the **evidence checklist** by
> dispute type, and §4.9 replaces the *first-90-days* section with **the first disputes**, because
> a dispute process is tested by cases, not by calendar. Declared; template 15 does not exist.

---

## 1. Purpose

A dispute in this ecosystem is not a customer-service event. It is **a hold on money**.

`AUT-MKP-11` blocks the disputed amount atomically the moment a dispute is raised. `BRU-BIL-03`
blocks the payout entirely while it stays open. `SLC-04` in `MD-018` makes that override the
configured hold period. So the elapsed time of the process **is** the cost to the counterparty,
and for an independent engineer who completed the job three weeks ago it is the whole
relationship.

Three facts make writing this down urgent rather than tidy:

| Fact | Consequence |
|---|---|
| **1000FiX decides, not the parties** (`BRU-ECM-09`) | We are the adjudicator, the counterparty and the payer at once. That is defensible only if the process is published, evidenced and appealable |
| **`G7-04` requires every dispute resolved within SLA** | An SLA exists per stage in `FR-MKP-059` and **no duration is stated anywhere in the repository** — `O-01` |
| **We remedy the customer first and recover from the seller second** (`BRU-MKP-20`) | The customer's dispute closes fast; the seller's exposure opens at the same moment, and they must be told how it will be decided |

**What this file is not.** It is not the agreement's dispute clause — `LG-004` §8, `LG-005` §8,
`LG-006` §8 and `LG-007` §8 each carry one. It is not customer complaint handling (`SP-028`), not
the internal marketplace procedure (`SP-024` §5.5), not seller sanctions and their appeal
(**`EO-002` §4.6**), and not the exit that a terminal dispute may lead to (**`EO-014`**).

---

## 2. Scope

**In scope.** Which disagreements are disputes and which are something else; the dispute types
across three ecosystems; intake — who may raise, how, and what a valid submission contains; the
evidence checklist per type; the money position at every stage; triage, evidence exchange,
mediation and decision; decision authority and segregation; the remedy set and how each is
executed; recovery from a counterparty and the limits on it; appeal; the external routes that
remain open regardless; publication of outcomes; and what the first cases must be reviewed for.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| The contractual dispute clause and governing law | `LG-004` §8, `LG-005` §8, `LG-006` §8, `LG-007` §8, `LG-003` |
| **Customer** complaints, escalation and compensation | `SP-028`; `M34` |
| Seller sanctions, the scorecard and the sanction appeal | **`EO-002` §4.5, §4.6** |
| The internal operator procedure | `SP-024` §5.5 |
| Warranty **claim** rejection and resubmission | **`EO-004` §4.7** — a rejected claim is not a dispute until it is escalated |
| Supplier **corrective action** | `EO-006` §4.1 stage 6; `FR-SRM2-031` |
| Corporate **invoice** disputes | `EO-007` §4.7; the contract and `LG-003` |
| Dispute reason-code values | `MD-026` |
| Payout mechanics and the statement | `M53`; `DT-039`, `DT-040` |
| Fraud, collusion and off-platform investigation | `FR-MKP-064`, `FR-MKP-065` — **an investigation is not a dispute** (§4.1) |
| Termination arising from a dispute | **`EO-014`** |

---

## 3. Audience

| Reader | Uses it for | Language |
|---|---|---|
| **Marketplace seller** | Raising a dispute, responding to one, and knowing when they will be paid | **Bengali** |
| **Supplier** | Escalating a rejection, a short payment or a scorecard fact | English |
| **Referral / alliance partner** | Escalating an attribution or commission decision | **Bengali** or English |
| **Customer** | Reference only — their route is `SP-028`, and it is faster |
| **Dispute Officer** *(new position under `R24`)* | The process they run |
| **Appeal decider** | The grounds, the evidence standard and the separation rule |
| **Finance Manager (`R26`)** | The money position at each stage, and the release authority |
| **Legal Counsel** | The external routes and the limits on our adjudication |

---

## 4. Content

### 4.1 What is a dispute — and what is not

The most useful thing this file does is refuse the wrong cases, because every wrongly-classified
case holds money that need not be held.

| It **is** a dispute | It is **not** a dispute — it is |
|---|---|
| A disagreement about the outcome, quality or value of a completed transaction | A **quality event** — raised as a nonconformity (`M23`, `SP-029`) |
| A challenge to a deduction, recovery or short payment | A **sanction**, appealed under `EO-002` §4.6 |
| A challenge to an attribution or commission calculation | A **claim rejection**, corrected and resubmitted under `EO-004` |
| A challenge to a rejection **after** the owning process has been exhausted | A **corrective action** under `EO-006` |
| A customer↔seller disagreement 1000FiX must adjudicate | A **trust-and-safety investigation** (`FR-MKP-064`, `FR-MKP-065`) — which is not adversarial and has no counterparty right of reply until an allegation is made |
| | A **customer complaint** — `SP-028`, and the customer route is faster and free |

> **A dispute is the escalation of last resort inside a relationship.** Raising one blocks money;
> raising one instead of using the owning process blocks money **unnecessarily**, and `DR-02`
> requires intake to say so at the point of raising.

### 4.2 The dispute journey

Lifecycle from `M12` §8.3. **The money column is the one every counterparty reads first.**

| # | Stage | What happens | Money position | SLA |
|---|---|---|---|---|
| **1** | **Raised** | Category, description, evidence and **desired remedy** submitted (`FR-MKP-058`) | **Disputed amount blocked atomically** (`AUT-MKP-11`) | — |
| **2** | **Triaged** | Validity, classification, whether the owning process was exhausted (§4.1) | Blocked | **`O-01`** |
| **3** | **Evidence exchange** | Both parties supply evidence against §4.4; each sees what the other has submitted | Blocked | **`O-01`** |
| **4** | **Mediation** | An attempt at an agreed outcome before a decision is imposed | Blocked | **`O-01`** |
| **5** | **Decided** | 1000FiX decides (`BRU-ECM-09`); decision and evidence recorded | Blocked | **`O-01`** |
| **6** | **Remedy executed** | The decided remedy is carried out; `M20`/`M01` instructed (`FR-MKP-061`, `AUT-MKP-12`) | **Released or recovered atomically** | — |
| **7** | **Closed** | Outcome recorded against `MD-026`; scorecard updated (`EO-002` §4.4) | Settled | — |
| — | **Withdrawn** | Raiser withdraws | **Released immediately** | — |
| — | **Appealed** | §4.7 | **Remains blocked** — `O-02` | **`O-01`** |
| — | **Final decision** | Not further appealable internally; external routes remain (§4.8) | Settled | — |

**Two properties of the money mechanic that must be stated to counterparties, not just built:**

- **Only the disputed amount is blocked**, not the whole balance. A seller with one disputed job
  is paid for the others (`FR-MKP-060`).
- **Blocking and release are atomic** (`T-07` in `M12`). There is no window in which an amount is
  both released and disputed, and no manual step that can strand it.

### 4.3 Dispute types across three ecosystems

| Ecosystem | Type | Raised by | Typical remedy |
|---|---|---|---|
| **Marketplace** | Job quality or incompleteness | Customer | Rework, partial refund, refund, goodwill |
| | Non-payment or short payment of earnings | Seller | Correction and release |
| | Deduction or recovery challenged | Seller | Reversal or reduction (`BRU-MKP-17`) |
| | Cancellation or no-show responsibility | Either | Fee reversal; score annotation |
| | Parts, provenance or warranty on a completed job | Customer | Rework or replacement; **counterfeit is not a dispute** — `BRU-MKP-11` |
| **Supplier** | Rejection at inspection challenged | Supplier | Reversal; scorecard **re-publication with a stated reason** (`BRU-SRM2-09`) |
| | Short payment or invoice deduction | Supplier | Correction |
| | Scorecard fact challenged | Supplier | Fact corrected at source in `M16`/`M41`; **never edited in `M42`** (`BRU-SRM2-08`) |
| | Price applied against the approved list | Either | Correction (`BRU-SRM2-14`) |
| **Partner** | **Attribution** — the largest partner category | Partner | Re-attribution where the fact is wrong; **never a discretionary award** (`BRU-PCM-04`) |
| | Commission calculation | Partner | Correction; `KPI-C40-04` is 100% accuracy |
| | Deal-registration refusal or conflict outcome | Partner | Review of the decision basis (`BRU-PCM-09`) |
| | Channel precedence | Partner | Decision per the declared rules (`BRU-PCM-10`) — **rules undecided**, `EO-009` `O-02` |

### 4.4 The evidence checklist

**A dispute is decided on the recorded evidence.** The checklist is published so a counterparty
can assemble a decidable case rather than an assertion.

| Dispute type | The raiser must supply | We already hold |
|---|---|---|
| **Job quality** | What is wrong, with photographs; what was expected; the desired remedy | The full evidence pack (`EO-002` §4.3): before/after, diagnostics, parts, QC, sign-off |
| **Non-payment / short payment** | The job reference and the amount expected | Wallet movements, commission, fees, holds, the statement (`DT-039`) |
| **Deduction or recovery** | Why it is disputed | The notice, the declared limit, the underlying remedy cost (`BRU-MKP-17`) |
| **Cancellation responsibility** | The account of what happened, with timestamps | Award, acceptance, messaging, location and status history |
| **Supplier rejection** | The reason it should not stand; batch and delivery references | Receipt, inspection record, reason code (`MD-026`), photographs |
| **Supplier short payment** | Invoice and PO references | Three-way match record, payment and remittance |
| **Scorecard fact** | The transaction reference and what is wrong with it | The `M16`/`M41` fact and its provenance |
| **Attribution** | The link or code used, the date, the consent record | Lead record, attribution stamp at creation, window evaluation (`T-02`, `T-03`) |
| **Commission** | The statement line disputed | Scheme version, rate, computation (`DT-040`) |

**Two rules about evidence, stated to both parties:**

| # | Rule |
|---|---|
| **E-1** | **Evidence created after the event carries less weight than evidence captured at the time.** This is why `EO-002` §4.3 exists and why a seller who captures the full pack is protected by it |
| **E-2** | **Each party sees the evidence the other submitted.** A decision made on evidence a party never saw is not defensible, and would not survive an external route (§4.8) |

### 4.5 Who decides, and the separation that makes it safe

| Decision | Who | Rule |
|---|---|---|
| Triage and classification | Dispute Officer (under `R24`) | `SP-024` §5.5 |
| Decision | Dispute Officer; **1000FiX decides, never the parties** | `BRU-ECM-09` |
| Release or recovery of the blocked amount | **Finance (`R26`)** — never the decider | `SP-024` §11; `SOD-06` |
| Appeal | **An operator who did not decide the original** | `BRU-MKP-18`, **`SOD-60`** |
| Recovery above the declared limit | CCO with CFO | `SP-024` §7 |
| Terminal outcome (removal) | CCO | `SP-024` §7 A-80 |

> **`SOD-60` has no compensating control at this scale.** `SP-024` §11 states it in terms: where
> the only available reviewer imposed the decision, **the appeal waits.** The counterparty's money
> waits with it. `EO-002` `O-05` records that `M12` §13 names only one new Dispute Officer
> position; **the same single point of failure sits under this file** — `O-03`.

### 4.6 Remedies

| Remedy | Used when | Executed by |
|---|---|---|
| **Rework** | The work can be put right | `M01`; the original seller or another |
| **Partial refund** | Value was delivered, but less than charged | `M20` (`FR-MKP-061`) |
| **Full refund** | No value delivered | `M20` |
| **Replacement** | A part or device must be replaced | `M15` / `M14` |
| **Goodwill** | No liability established but the relationship warrants it | `M20`; **recorded as goodwill, never as an admission** |
| **Correction and release** | The dispute was a computation or fact error | `M53` |
| **Re-attribution** | The attribution fact was wrong | `M40` |
| **No remedy** | The case is not made out | — |

**Recovery from a counterparty** (`FR-MKP-063`, `BRU-MKP-17`) requires **notice, a declared limit
and a right of appeal** — all three, every time. **The limit is unconfigured** (`M12` Q-03) —
`O-04`.

**1000FiX-first remediation** (`BRU-MKP-20`) is stated to sellers in `EO-001` §4.6 and restated
here from the seller's side: the customer is made whole immediately, **and that is not itself a
finding against the seller.** The recovery question is decided separately, on evidence, under this
file. Conflating the two — remedying the customer and debiting the seller in one action — is the
commonest way a marketplace loses supply, and `DR-08` prohibits it.

### 4.7 Appeal

| Element | Position |
|---|---|
| Who may appeal | Either party to the decision |
| Grounds | The evidence was misread; evidence was not considered; the process was not followed; the remedy does not match the decision |
| **Not grounds** | Disagreement with a rule, a rate or a threshold. Those are policy routes — `EO-011`, `EO-002` §4.6 |
| Decider | **An operator who did not decide the original** (`BRU-MKP-18`, `SOD-60`) |
| Window and service level | **Undecided** — `O-01`, `O-02` |
| Money | **Remains blocked during appeal** — see `O-02`; this is the single harshest interaction in the file |
| Outcome | Upheld, varied or reversed, with the record annotated and the scorecard corrected |
| After | Internally final; §4.8 remains |

### 4.8 The routes that stay open regardless

**Stated in the content, deliberately.** A private dispute process presented as the only route
invites a challenge to its enforceability, and none of these routes is ours to close.

| Route | Who | What this file must respect |
|---|---|---|
| **The agreement's dispute clause** | Any counterparty | `LG-004` §8, `LG-005` §8, `LG-006` §8, `LG-007` §8 — governing law, forum and escalation |
| **Directorate of National Consumer Rights Protection (DNCRP)** | A consumer | Under the Consumers' Right Protection Act 2009 §60, a complaint must be made **within 30 days of the cause of action arising**, in writing, with the receipt annexed. **Our internal process must not consume that window** — `DR-11` |
| **The platform's own 72-hour obligation** | A consumer complaining about the platform | The Digital Commerce Operation Guidelines 2021 require an e-commerce entity to resolve complaints against itself **within 72 hours** and to appoint a compliance officer coordinating with the DNCRP. **No 72-hour path exists in §4.2** — `O-05` |
| **Civil remedies** | Any party | Unaffected |

> **Two external timings bound this process and neither is currently reflected in it.** A
> multi-stage internal process with unstated SLAs can easily run past 30 days, at which point a
> consumer who waited for us has lost their statutory complaint window. Both facts here rest on
> authoritative **secondary** sources (`class: P2`); `CG-012` `EV-01` would demand a primary
> instrument for Class A content, and although this file is class `D`, **`O-05` treats these as
> requiring `CG-007` `G6`-equivalent verification because a timing obligation cannot be
> approximated.**

### 4.9 The first disputes

| Case | What to review | What it proves |
|---|---|---|
| **First** | Was it a dispute at all, or should §4.1 have routed it elsewhere? | Whether intake is filtering |
| **First** | How long did each stage take, against an SLA that does not yet exist? | The baseline `O-01` needs |
| **First five** | Did the counterparty submit the §4.4 evidence without being asked twice? | Whether the checklist is reaching them |
| **First appeal** | Was a second operator available, or did the appeal wait? | `SOD-60`, `O-03` |
| **First ten** | Total days money was blocked, per case, per party | **The only number that matters to a counterparty** |
| **First ten** | Outcome distribution by reason code | Whether disputes are concentrated in one cause — a process defect, not a counterparty defect |

**A dispute rate below `KPI-081`'s 1.5% with a long resolution time is worse than a slightly
higher rate resolved quickly**, and the review must be able to say which is happening.

### 4.10 Rules

| # | Rule |
|---|---|
| **DR-01** | Every stage states **what happens to the money**, not only what happens to the case |
| **DR-02** | Intake states, at the point of raising, that a dispute blocks money and that the owning process (§4.1) is faster where it applies |
| **DR-03** | Only the **disputed amount** is blocked; the rest of a balance is paid (`FR-MKP-060`) |
| **DR-04** | The decision and its evidence are recorded, always (`BRU-ECM-09`) |
| **DR-05** | Each party sees the evidence the other submitted (`E-2`) |
| **DR-06** | Deciding and releasing are different people (`SOD-06`); deciding and hearing the appeal are different people (`SOD-60`) |
| **DR-07** | Recovery requires **notice, a declared limit and an appeal right** — all three (`BRU-MKP-17`) |
| **DR-08** | **Remedying the customer is not a finding against the seller.** The two decisions are separated in the record and in the communication (`BRU-MKP-20`) |
| **DR-09** | A supplier scorecard correction is a **re-publication with a stated reason**, never an edit (`BRU-SRM2-09`); an attribution correction is a **fact** correction, never a discretionary award (`BRU-PCM-04`) |
| **DR-10** | A goodwill remedy is recorded as goodwill and is not an admission of liability |
| **DR-11** | **The external routes in §4.8 are stated in the content**, including the 30-day statutory complaint window, and the internal process is designed not to consume it |
| **DR-12** | Outcomes are coded against `MD-026`. Free text cannot be counted, and `G7-04` requires a countable answer |
| **DR-13** | Precedent-setting decisions are logged in **`RF-006`**, so a second similar case is decided the same way |
| **DR-14** | Bengali is required for the seller-facing content; a party who cannot read the process cannot use it (`CP-05`) |
| **DR-15** | Where a stage SLA is unset, the content **says it is unset** rather than implying a timescale (`O-01`) |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`LG-004`](../10_Legal_Policy_and_Compliance/LG-004_Marketplace_Seller_Agreement_and_Policy_Handbook.md) §8, [`LG-005`](../10_Legal_Policy_and_Compliance/LG-005_Brand_Partner_Portal_Terms.md) §8, [`LG-006`](../10_Legal_Policy_and_Compliance/LG-006_Vendor_Portal_Terms_and_Supplier_Code_of_Conduct.md) §8, `LG-007` §8 | The contractual dispute clauses this process sits inside |
| `M12` §5.6, §8.3, §11 | The workflow, lifecycle, blocking and remedy automation |
| `M42` `FR-SRM2-031`, `BRU-SRM2-08`, `BRU-SRM2-09` | Supplier corrective action and the scorecard-correction rule |
| `M40` `FR-PCM-024`, `FR-PCM-027`, `FR-PCM-029` | Attribution, deal registration and channel precedence |
| `M20`, `M53` | Remedy execution, release and recovery |
| `M23`, [`SP-029`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) | Where a dispute reveals a nonconformity |
| [`SP-024`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-024_SOP_Marketplace_Seller_Onboarding_and_Governance.md) §5.5, §7, §11 | The operator procedure, authority limits and segregation |
| [`SP-028`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-028_SOP_Complaint_Escalation_and_Compensation.md) | The customer complaint route, which is faster and separate |
| [`SP-004`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md), [`SP-005`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md) | Approval limits and escalation |
| [`MD-026`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md) | Dispute and outcome reason codes |
| [`EO-002`](EO-002_Seller_Standards_Scoring_and_Sanctions_Handbook.md) | Sanctions and their appeal — the process this one must not be confused with |
| [`EO-004`](EO-004_Brand_Claim_Rules_and_Evidence_Standard_Guide.md), [`EO-006`](EO-006_Supplier_Performance_Scorecard_Explanation.md), [`EO-009`](EO-009_Referral_and_Alliance_Partner_Kit.md) | The owning processes §4.1 routes cases back to |
| [`EO-011`](EO-011_Rate_Card_and_Pricing_Communication_Pack.md) | Where a price change is the underlying cause |
| [`EO-014`](EO-014_Ecosystem_Offboarding_and_Exit_Content.md) | Where a dispute becomes a termination |
| [`UI-017`](../03_UI_Copy_and_Microcopy/03B_Portals/UI-017_P07_Marketplace_Seller_Portal_UI_Copy_Pack.md), [`UI-034`](../03_UI_Copy_and_Microcopy/03C_Admin_Workspaces/UI-034_Workspace_Marketplace_Console_Copy.md), [`HC-009`](../09_Help_Centre_and_Self_Service/09A_Help_Sets_By_Portal/HC-009_Help_Set_P07_Marketplace_Seller_Portal.md), `NT-012` | The party surfaces, the operator console, help and notices |
| [`DT-039`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-039_Marketplace_Seller_Payout_Statement.md), [`DT-040`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-040_Partner_Commission_Statement.md) | The statements a money dispute is argued from |
| **`RF-006`** | Precedent log — **unwritten** |

> **Rule-citation attribution.** **BRU-MKP-\***  → `M12` §9 · **BRU-PCM-\***  → `M40` §9 · **BRU-SRM2-\***  → `M42` §9 — these are **module-scoped** rule families and **`05-05` carries none of them**. The families this file cites that **do** resolve in `05-05` are `BRU-BIL-*`, `BRU-ECM-*`. Stated per `AUDIT-015` R-11, which asked that the convention be recorded once rather than rediscovered by each extraction.

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Monthly for the first two quarters after W7 launch; quarterly thereafter |
| Trigger for out-of-cycle review | Stage SLAs being set; an appeal that waits for want of a second operator; a dispute reaching an external forum; a change to any `LG` §8 clause; a change to DNCRP or Digital Commerce guidance; a reason code appearing that §4.3 does not cover; `KPI-081` moving more than 0.5 points |
| Owner | Marketplace Operations with Legal Counsel; Finance for the money positions |
| Change control | **A change to the money position at any stage, or to the appeal route, requires CCO, CFO and Legal Counsel sign-off.** Both alter what a counterparty is entitled to |
| Effectiveness measure | **Median and 90th-percentile days money is blocked, per ecosystem** — not the dispute rate, which can fall because the process is unusable |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`G7-04` requires every dispute resolved within SLA and no SLA exists.** `FR-MKP-059` specifies *"an SLA at each stage"*; **no duration for triage, evidence exchange, mediation, decision or appeal is stated in `M12`, `05-05`, `06-02`, `SP-024` or any `LG` file.** §4.2 therefore carries five stages and five blanks, `DR-15` requires the file to say so, and **the gate criterion is unmeasurable as written** — the same defect class `AUDIT-014` TS-18 `O-07` found in two other `06-02` criteria | CCO with Legal Counsel and Marketplace Operations | **W7 — before the first dispute** |
| **O-02** | **Money stays blocked during appeal and nothing caps the total.** §4.2 and §4.7 block funds from raise to final decision. Against that, the Digital Commerce Operation Guidelines 2021 require a marketplace to settle to the business owner **within ten days** of deducting charges and commission. **A dispute plus an appeal, both without SLAs, will exceed ten days routinely.** `EO-001` `O-01` and `EO-014` record the same conflict from the onboarding and exit sides — **one legal question, three files** | **Legal Counsel with CFO**, external adviser | **W6 — before the first payout** |
| **O-03** | **There is one Dispute Officer position and two separation rules that each require a second person.** `SOD-06` separates deciding from releasing; `SOD-60` separates deciding from hearing the appeal. `M12` §13 names *"Dispute Officer (new position under R24)"* — **singular** — and `SP-024` §11 records that where no second operator exists **"the appeal waits"** with **no compensating control**. At 500–2,000 sellers and a 1.5% dispute rate, the appeal queue is not hypothetical | Programme Manager with CCO | **W7 — before launch** |
| **O-04** | **The recovery limit is undecided** (`M12` Q-03, with the security-deposit question). `BRU-MKP-17` requires a **declared** limit and §4.6 cannot declare it. **A recovery with no stated ceiling is the term a seller will refuse to accept, and it is in `LG-004` §4.6, which is itself marked pending** | CFO / CCO | **W7 build** |
| **O-05** | **Two external obligations bound this process and neither is reflected in it.** The Digital Commerce Operation Guidelines 2021 impose a **72-hour** resolution for complaints against the platform and require a **compliance officer** coordinating with the DNCRP; the Consumers' Right Protection Act 2009 §60 gives a consumer **30 days** from the cause of action to complain to the Directorate. **§4.2 has no 72-hour path, no compliance-officer role is named anywhere in the programme, and no rule prevents the internal process consuming the 30-day window.** Both sources are `class: P2`; **a timing obligation cannot rest on secondary reporting** and needs `G6`-equivalent verification against the instruments | **Legal Counsel with CCO**, external verification | **W6 — before the marketplace opens to consumers** |
| **O-06** | **`RF-006` is unwritten and `DR-13` requires precedent-setting decisions logged there.** Without it, the second similar dispute is decided by whoever is on duty, and `BRU-ECM-09`'s recorded-decision requirement produces a pile of records with no doctrine. **Third Category-18 file blocked by `RF-006`**, after `EO-011` `O-03` and `EO-012` `CB-13`; `AUDIT-014` TS-12 recorded the same for `TS-018` | Programme Content Lead | **W1** |
| **O-07** | **Bengali is required and unresourced.** The largest disputing population is Bengali-reading and `DR-14` makes the process unusable without it. **`CG-010` §3.2's `EO` rationale does not name disputes**, and this file's bilingual status derives from the §3.3 audience rule | Localisation Lead *(unappointed)* with Marketplace Operations | **W7 minus 6 weeks** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the first-90-days addition replaced by **the first disputes** and the substitution declared
- [x] **A dispute framed as a hold on money, with the money position stated at every stage**
- [x] Six categories of case explicitly excluded and routed to their owning process
- [x] Full lifecycle from `M12` §8.3, with the atomic blocking and partial-balance properties stated to counterparties
- [x] Dispute types enumerated across all three ecosystems with their typical remedies
- [x] Evidence checklist per type, split into what the raiser supplies and what we already hold
- [x] Decision authority table with both segregation rules, and the absence of a compensating control stated
- [x] Eight remedies, with recovery's three mandatory conditions and the customer-first separation rule
- [x] Appeal route with the grounds that are **not** grounds
- [x] **The external routes stated in the content, including the 30-day statutory window the internal process must not consume**
- [x] First-disputes review whose headline measure is days money was blocked
- [x] Fifteen rules
- [x] All internal links resolve
- [x] Seven open items recorded
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` no stage SLA exists and `G7-04` requires one — outstanding; five stages carry five blanks**
- [ ] **`O-02` money blocked through appeal against a ten-day statutory settlement obligation — outstanding**
- [ ] **`O-03` one Dispute Officer, two separation rules — outstanding; the appeal waits and so does the money**
- [ ] **`O-05` 72-hour and 30-day external obligations unreflected and unverified against primary instruments — outstanding**
- [ ] **`O-06` `RF-006` unwritten — outstanding; third Category-18 file blocked by it**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Named approver recorded — **pending Content Design Lead with Legal Counsel**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
