---
id: EO-002
title: Seller Standards, Scoring and Sanctions Handbook
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Marketplace Operations with Quality
author: Marketplace Operations with Quality Manager and Legal Counsel
reviewers: [Chief Commercial Officer, Quality Manager, Chief Financial Officer, Data Protection Officer, Content Design Lead, Localisation Lead, Operations Director]
approver: Legal Counsel
content_class: B
purpose: >
  The standards a marketplace seller is held to, how the composite score is computed from them,
  what each threshold does, and what a sanction means, when it applies, and how it is appealed.
  Marketplace job standards are identical to owned jobs, and consequences apply automatically as
  score thresholds are crossed. A consequence applied under a standard the seller was never given
  in writing is a wrongful suspension: the seller loses income, the platform loses supply, and
  1000FiX loses the argument. This handbook is incorporated into the seller agreement by
  reference, which is why it is a contractual instrument rather than guidance.
traces_to: [P07, M12, M23, M53, 04-00 P07, 05-04 §6 SOD-06, 05-04 §8 EA-04, 05-05 §8 BRU-ECM-02, BRU-ECM-03, BRU-ECM-04, BRU-ECM-06, BRU-ECM-07, BRU-ECM-08, BRU-ECM-09, BRU-MKP-02, BRU-MKP-06, BRU-MKP-11, BRU-MKP-12, BRU-MKP-13, BRU-MKP-17, BRU-MKP-18, BRU-MKP-20, FR-MKP-040, FR-MKP-047, FR-MKP-048, FR-MKP-049, FR-MKP-050, FR-MKP-051, FR-MKP-052, FR-MKP-053, FR-MKP-054, FR-MKP-055, FR-MKP-056, FR-MKP-057, FR-MKP-063, FR-MKP-064, FR-MKP-066, FR-MKP-077, AUT-MKP-13, KPI-C12-06, KPI-C12-09, KPI-C12-10, KPI-C12-11, KPI-C12-15, KPI-081, G7-03, G7-04, MD-018, MD-026, LG-004, SP-024, SP-028, SP-029, UI-017, UI-034, HC-009, TR-019, NT-012, EO-001, EO-013, EO-014]
priority: P2
wave: W7
bilingual: yes
bn_counterpart: EO-002_Seller_Standards_Scoring_and_Sanctions_Handbook_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M12_Marketplace_and_Seller_Ecosystem.md §5.5 FR-MKP-049…057 scorecard and consequence ladder, §5.4 FR-MKP-040 evidence parity, §5.6 FR-MKP-063…067, §8.1 transition guards, §9 BRU-MKP-02/06/11/12/13/17/18/20, §11 AUT-MKP-13
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P07 governance requirements 2 and 4; "quality and evidence standards for marketplace jobs are identical to owned jobs"; "falling below the performance threshold reduces visibility automatically, then suspends"
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md §8 BRU-ECM-02, BRU-ECM-03, BRU-ECM-04, BRU-ECM-06, BRU-ECM-07, BRU-ECM-08, BRU-ECM-09
    verified: 2026-08-18
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-018_Marketplace_Seller_Category_and_Standard_Register.md §2 min_rating_to_operate, suspension_rating, max_open_jobs; §4 SLC-02 and SLC-05 — lowering the suspension rating requires CCO and Legal approval because it changes contractual grounds
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §2.9 KPI-081 marketplace dispute rate < 1.5%; §4 Gate 7 G7-03 marketplace jobs meeting the same quality and evidence standards as owned jobs, G7-04 dispute rate below target with all disputes resolved within SLA
    verified: 2026-08-18
    class: P1
  - source: ISO 9001:2015 clause 8.4 — control of externally provided processes; 8.4.2 the extent of control applied where an external provider performs a process on the organisation's behalf; 8.7 control of nonconforming outputs
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Seller Standards, Scoring and Sanctions Handbook

| Item | Value |
|---|---|
| Audience | All marketplace sellers — provisional, approved, restricted, on probation |
| Population | **500–2,000** sellers (`04-00` P07) |
| Contractual status | **Incorporated into `LG-004` by reference** (`LG-004` §4.9 Policy Handbook) |
| Content class | **B — legal / contractual.** Approver: Legal Counsel (`CG-002` §4) |
| Portal | `P07`; the operator side is `UI-034` Marketplace Console |
| Wave | W7 · Months 27–30 |
| Gate criteria evidenced | `G7-03` quality parity · `G7-04` dispute rate and SLA |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3), all
> six sections in order. The three `EO` additions are applied to this file's subject rather than
> to an admission process: the **journey table** (§4.1) is the *standing* journey a seller travels
> under the scorecard; the **checklist** (§4.3) is the per-job evidence checklist that the standard
> is actually made of; the **first-90-days section** (§4.7) is the cold-start problem — how a
> seller with no volume is scored. The adaptation is declared here because `CG-009` §3 does not
> anticipate it and template 15 `TPL_Onboarding_Kit.md` does not exist.

---

## 1. Purpose

`04-00`'s P07 governance requirements contain two sentences that together create every obligation
in this file:

> *"Quality and evidence standards for marketplace jobs are identical to owned jobs."*
> *"Falling below the performance threshold reduces visibility automatically, then suspends."*

The first is a standard. The second is an **automatic consequence** — `AUT-MKP-13` applies it when
a score crosses a threshold, with no operator in the loop. A machine reducing a person's income
without a human decision is defensible only if three things are true, and this handbook exists to
make them true:

| Condition | Where it is discharged |
|---|---|
| The standard was given to the seller in writing, in their language, before it was applied | This file, bilingual, incorporated into `LG-004` |
| The measurement is stated — what is counted, over what window, with what weight | §4.4 |
| There is a route to challenge, decided by someone other than the person or process that imposed it | §4.6; `BRU-MKP-18`, `SOD-60` |

**Why it is a Class B file and not a `D` guide.** `MD-018` `SLC-05` states the point precisely:
lowering the suspension rating *"requires CCO and Legal approval — it changes contractual
grounds"*. If the thresholds are contractual grounds, the document that explains them is a
contractual instrument. `CG-002` §6 anticipates this — the `EO` approver class is *"D (B for
agreements)"* — and this is one of the two `EO` files that takes the B route.

---

## 2. Scope

**In scope.** The service and evidence standards applying to a marketplace job; the conduct
standards applying to a seller; the scorecard's components, windows and weighting model; each
threshold and what it triggers; the full sanction ladder from visibility reduction to removal;
probation and remediation; recovery against earnings; the appeal route and who may decide it;
review integrity; and the specific breaches that bypass the ladder entirely.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| Registration, verification and admission | `EO-001` |
| The agreement, its liability terms and its termination clauses | `LG-004` |
| The threshold **values** — `min_rating_to_operate`, `suspension_rating`, `max_open_jobs`, `payout_hold_days` | **`MD-018`.** This file explains the mechanism; the register holds the numbers |
| Dispute intake, evidence exchange, mediation and decision | **`EO-013`** |
| Offboarding, final settlement and reinstatement after removal | **`EO-014`** |
| The internal operator procedure for imposing and reviewing sanctions | `SP-024` §5.4 |
| Nonconformity and CAPA arising from sampled seller work | `M23`; `SP-029` |
| Customer complaints about a seller job | `SP-028` — the customer path; the seller consequence path is here |
| Scorecard screen copy and the seller's own performance view | `UI-017`; operator view `UI-034` |
| Notification wording for each consequence | `NT-012` |
| Reason-code values behind every rejection and sanction | `MD-026` |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Seller** | Knowing what is measured, what the number means, and what happens next |
| **Marketplace Operations (`R24`)** | The basis on which a sanction is imposed and defended |
| **Appeal decider** — an operator who did not impose the sanction | The grounds and the evidence standard for overturning |
| **Quality Manager (`R32`)** | The parity claim, and the sampling that evidences it (`G7-03`) |
| **Legal Counsel** | Confirming every sanction has a contractual basis in `LG-004` |
| **Contact Centre (`R34`)** | Explaining a consequence to a seller who has just been told about it |
| **Brand partners** | Evidence that work done under the 1000FiX name by third parties is controlled (`ISO 9001` 8.4.2) |

---

## 4. Content

### 4.1 The standing journey

Rendered from `M12` §8.1. Every arrow is either a rule in §4.5 or a decision in §4.6.

| Standing | How a seller reaches it | What it costs them | What returns them |
|---|---|---|---|
| **Provisional** | On approval (`EO-001`) | Limited job value; closer monitoring | Graduation — §4.7 |
| **Approved** | Graduation guard met | — | — |
| **Restricted** | Score below a category threshold, **or** a category certification lapsed | Cannot list or bid **in the affected category only** | Score recovery, or certification renewal |
| **Probation** | Score below threshold with a remediation plan issued (`FR-MKP-054`) | Reduced visibility; a review date; required training | Remediation verified |
| **Suspended** | Terminal-severity breach, upheld serious dispute, or counterfeit finding | **Cannot transact at all.** Customer-data access revoked immediately | Reinstatement after remediation, or a successful appeal |
| **Expired** | A document or registration lapsed (`BRU-ECM-08`) | Cannot transact | Renewal. **Standing is not otherwise changed** |
| **Offboarding / Removed** | Terminal breach or voluntary exit | Covered by `EO-014` | Reinstatement terms in `EO-014` |

> **Restricted is per category; suspended is per seller.** The distinction matters commercially:
> a seller restricted in one category keeps earning in the others, which is why `FR-MKP-053`
> places category restriction *below* suspension on the ladder rather than treating both as "off".

### 4.2 The standard — what a marketplace job must be

The standard is not a marketplace standard. It is the 1000FiX standard, applied to a marketplace
job, and the handbook says so in the seller's own interest.

| # | Standard | Rule | Enforcement |
|---|---|---|---|
| 1 | The job is executed by the approved seller, in a category they are qualified in | `BRU-ECM-07` | Hard block on listing and bidding |
| 2 | **The evidence pack is identical to an owned job** — before/after photographs, diagnostic record, QC checklist | `BRU-ECM-03`, `FR-MKP-040` | **Completion blocked without it** |
| 3 | Customer verification, signature or OTP at completion | `FR-MKP-041` | Hard block |
| 4 | Parts used are declared with their provenance grade and any warranty, and the customer is told | `FR-MKP-042` | Declaration required at completion |
| 5 | Genuine parts where the category requires them; **no counterfeit or non-genuine parts, ever** | `BRU-MKP-11` | Immediate listing suspension and investigation — **not a ladder step** |
| 6 | The declared warranty on the work is honoured by the declared party | `FR-MKP-045` | Claim routing |
| 7 | Customer contact data is used **only for the awarded job** and only within the grant window | `EA-04`, `BRU-ECM-05` | Automatic revocation; misuse is a data-protection incident |
| 8 | Communication with the customer stays on the platform; contact-detail exchange is masked | `FR-MKP-046`, `T-10` | Detection, then §4.5 `SS-11` |
| 9 | The job is not taken off-platform | `FR-MKP-064` | Trust-and-safety investigation |
| 10 | Reviews are earned, never solicited by inducement or manufactured | `BRU-ECM-02`, `FR-MKP-051` | Review removal and sanction |
| 11 | Escalation to 1000FiX where the job cannot be completed safely or correctly | `FR-MKP-044` | Non-escalation is itself a finding |
| 12 | Health, safety and conduct on customer premises | `LG-004` §4.3 | Safety breaches bypass the ladder — §4.5 `SS-13` |

### 4.3 The evidence checklist

This is what "identical to an owned job" means, item by item. It is reproduced here because
**the parity claim is unfalsifiable without it**, and `G7-03` requires the parity to be
demonstrated at the Wave 7 gate.

| Artefact | Owned job | Marketplace job | Blocking |
|---|:--:|:--:|:--:|
| Device and fault identification recorded against the taxonomy | ✔ | ✔ | Yes |
| **Before** photographs, GPS- and time-stamped | ✔ | ✔ | **Yes** |
| Diagnostic record / fault code | ✔ | ✔ | Yes |
| Parts consumed, with provenance grade | ✔ | ✔ | Yes |
| QC checklist for the job type | ✔ | ✔ | **Yes** |
| **After** photographs | ✔ | ✔ | **Yes** |
| Test results where the job type requires them | ✔ | ✔ | Yes |
| Time recorded (start, pause, resume, stop) | ✔ | ✔ | No — scored, not blocking |
| Customer sign-off — signature or OTP | ✔ | ✔ | **Yes** |
| Warranty statement issued to the customer | ✔ | ✔ | Yes |

**Two differences, both in the seller's favour, both stated so they are not mistaken for
leniency.** First, a seller may escalate a job to 1000FiX at any point and hand it over without a
completion penalty where the escalation is justified (`FR-MKP-044`). Second, where the customer's
experience requires it, **1000FiX remedies first and recovers from the seller second**
(`BRU-MKP-20`) — the seller is not left facing an angry customer alone. Recovery is then subject
to §4.5 `SS-12`.

### 4.4 How the score is computed

`FR-MKP-052` names the components. This handbook states what each one counts and — critically —
**what it does not count**, because a seller's first assumption about any score is that it
punishes them for things outside their control.

| Component | What is counted | What is deliberately **not** counted |
|---|---|---|
| **Acceptance rate** | Awards accepted within the acceptance window | Broadcasts the seller never saw; jobs outside their declared hours or areas |
| **On-time rate** | Arrival and completion against the seller's own committed ETA | Delays caused by customer unavailability, recorded as such |
| **Completion rate** | Accepted jobs carried to customer sign-off | Jobs 1000FiX takes over after a justified escalation |
| **Average rating** | Customer ratings from **completed transactions only** (`BRU-ECM-02`) | Unverified reviews; reviews removed under `FR-MKP-051` |
| **Rework rate** | Return visits attributable to the original work (`FR-MKP-047`) | Rework caused by a part failure under warranty, where the part was declared and genuine |
| **Dispute rate** | Disputes **upheld against the seller** (`EO-013`) | Disputes raised and withdrawn, or decided in the seller's favour |
| **Evidence compliance** | The §4.3 blocking artefacts, present and legible | —. `KPI-C12-09` targets **100%** at W9; there is no tolerance to describe |

**Weighting, window and grain.** The composite (`fix.seller.score`) is computed per period per
seller. **The weights, the period length and the minimum job count for a stable score are
unconfigured** — `O-01`. The handbook states the model and marks the numbers as set at launch;
`SS-02` forbids it from estimating them.

**The score is explainable or it is not usable.** `FR-MKP-056` requires the seller to see their
own score, its components, their standing and the consequence of falling further. This handbook
adds the reciprocal obligation: **any score shown to a seller decomposes into the components
above, for the period stated.** A composite with no decomposition is a number a seller cannot act
on and cannot dispute, and `EO-013` would have nothing to adjudicate.

### 4.5 The sanction ladder

| Step | Sanction | Trigger | Applied by | Reversible by |
|---|---|---|---|---|
| **0** | **Notice** — the score has moved toward a threshold | Approach to threshold | System, informational | — |
| **1** | **Visibility reduction** | Score below `min_rating_to_operate` (`MD-018`) | **Automatic** (`AUT-MKP-13`, `BRU-ECM-04`) | Score recovery |
| **2** | **Category restriction** | Category-specific score, or a lapsed certification | Automatic | Recovery or renewal |
| **3** | **Probation with a remediation plan** | Sustained sub-threshold performance | `R24`, with a plan, required training and a review date (`FR-MKP-054`) | Verified remediation |
| **4** | **Suspension** | Below `suspension_rating`; or a §4.5.1 trigger | Automatic on threshold; `R24` + CCO on a §4.5.1 trigger (`SP-024` §7) | Appeal, or verified remediation |
| **5** | **Removal** | Terminal breach, or repeated suspension | CCO (`SP-024` §7 A-80) | `EO-014` reinstatement terms only |

#### 4.5.1 Breaches that bypass the ladder

Stated separately because a ladder implies gradualism, and these are not gradual:

| Breach | Immediate consequence | Rule |
|---|---|---|
| **Counterfeit or non-genuine part supplied** | Listing suspended immediately; seller suspended pending investigation | `BRU-MKP-11`, `AUT-MKP-16` |
| **Safety incident or harm to a person or property** | Suspend first, investigate second. *"Safety is not a performance conversation"* | `SP-024` §6 |
| **Customer-data misuse or retention beyond the grant window** | Access revoked; treated as a data-protection incident, not only a contract breach | `EA-04`; `LG-008` |
| **Verified identity fraud** — the account is not the verified person | Suspension and removal; no reapplication | `EO-001` §4.3 |
| **Systematic off-platform transacting** | Trust-and-safety investigation, then policy consequence | `FR-MKP-064`; **the consequence is undecided** — `O-03` |
| **Review manipulation** | Reviews removed; sanction per severity | `FR-MKP-051`, `BRU-ECM-02` |

#### 4.5.2 The rules that constrain the sanctioner

These bind 1000FiX, not the seller, and they are in the handbook because a seller who cannot see
the constraints on the platform does not believe there are any.

| # | Rule |
|---|---|
| **SS-01** | Every sanction states its trigger, the evidence, the period measured, and the route to appeal, at the moment it is applied (`AUT-MKP-13`) |
| **SS-02** | This handbook never states a threshold value. `MD-018` holds them; a value quoted here and changed there is a seller told the wrong contractual ground |
| **SS-03** | A threshold change is **effective-dated and notified in advance**; it is never applied to a period already measured. `MD-018` `SLC-05` requires CCO and Legal approval to lower `suspension_rating` |
| **SS-04** | **An automatic sanction is reviewed weekly by a human for data defects** (`SP-024` §5.3 step 12). A wrongly suspended seller loses income and trust, and the system cannot tell the difference between poor performance and a broken feed |
| **SS-05** | **Paid promotion never overrides a quality-based restriction or suppression** (`BRU-MKP-12`). Visibility cannot be bought back |
| **SS-06** | Promoted placements are marked as promoted to the customer (`BRU-MKP-13`, `FR-MKP-077`) |
| **SS-07** | Only customers with a completed transaction may review (`BRU-ECM-02`); the seller has **one** response per review (`FR-MKP-050`) |
| **SS-08** | A seller sees their own score and its components; they never see another seller's, and never 1000FiX cost or margin (`M12` §13) |
| **SS-09** | Approving a seller and approving that seller's payout remain separate people throughout the sanction process (`SOD-06`) |
| **SS-10** | **An appeal is decided by an operator other than the one who imposed the sanction** (`BRU-MKP-18`, `SOD-60`). Where no second operator is available, **the appeal waits** — `SP-024` §11 records that this has no compensating control |
| **SS-11** | Detection signals (contact exchange, cancellation patterns, repeat pairs) create an **investigation**, never an automatic sanction. `M12` rejected "aggressive surveillance approaches incompatible with PDPA 2026 and with treating sellers as partners" |
| **SS-12** | Recovery of a remedy cost from seller earnings requires **notice, a declared limit and a right of appeal** (`BRU-MKP-17`) |
| **SS-13** | A safety-related suspension is not scored, negotiated or laddered |
| **SS-14** | Sanction and reinstatement decisions are recorded with actor, reason and evidence, and are retrievable for the retention period |
| **SS-15** | High performance has consequences too: visibility weighting, badges and tier advancement (`FR-MKP-057`). A ladder with only downward steps reads as a penalty regime |

### 4.6 Appeal

| Stage | Who | Timebox | Rule |
|---|---|---|---|
| Notice of sanction | System / `R24` | At application | `AUT-MKP-13` |
| Appeal submitted with evidence | Seller | Stated in `LG-004`; **the window is undecided** — `O-04` | `FR-MKP-055` |
| Decision | **An operator who did not impose the sanction** | Stated in `LG-004` | `BRU-MKP-18`, `SOD-60` |
| Outcome | Upheld, varied, or reversed with the standing restored and the record annotated | — | `SS-14` |
| Escalation | CCO | On refusal | `SP-024` §7 |

**What an appeal can and cannot do.** It can show the measurement was wrong, the evidence was
misread, or a component counted something §4.4 says it does not count. It cannot re-argue the
threshold — that is a change to `MD-018` requiring CCO and Legal approval under `SLC-05`, and it
is a policy route, not an appeal route.

> **The external route is not closed by this handbook.** A seller remains free to complain to the
> Directorate of National Consumer Rights Protection or to pursue contractual remedies; nothing
> here waives that, and `LG-004` §8 governs dispute resolution between the parties. Stated
> because a handbook that appears to be the only route invites a challenge to its enforceability.

### 4.7 The first 90 days under the scorecard

The cold-start problem is real and is the commonest cause of unfair-feeling scores on any
marketplace: **a seller with three jobs has a rating computed from three data points.** One
dissatisfied customer moves a three-job seller below a suspension threshold that a
three-hundred-job seller would absorb.

| Days | What is measured | What is not yet used against the seller |
|---|---|---|
| **0–30** | Evidence compliance (**from job one — it is binary, not statistical**); acceptance; on-time | Average rating; rework rate; dispute rate — all volume-dependent |
| **31–60** | The above, plus rating once the minimum job count is reached | Composite-driven automatic sanctions |
| **61–90** | Full composite; graduation review at the `M12` §8.1 guard | — |
| **Throughout** | §4.5.1 bypass triggers apply **from job one**. Safety and counterfeit are not volume-dependent | — |

**The minimum job count for a stable score is unconfigured** (`O-01`). Until it is set, a
provisional seller is protected by the provisional job-value limit rather than by a scoring rule,
which is a weaker control and is recorded as such.

**Recognition in the first 90 days matters as much as sanction.** `KPI-C12-05` targets a monthly
active rate above 70% and `KPI-C12-07` a 12-month retention above 65%. A new seller who meets the
evidence standard on their first ten jobs should see it reflected in visibility, because the
alternative — a ladder that only descends — teaches sellers that the score is a threat.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`LG-004`](../10_Legal_Policy_and_Compliance/LG-004_Marketplace_Seller_Agreement_and_Policy_Handbook.md) §4.8, §4.9 | The contractual hook. This handbook is incorporated by reference; **`LG-004` §4.8 is itself marked *pending `O-03`*** |
| [`MD-018`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-018_Marketplace_Seller_Category_and_Standard_Register.md) | Every threshold value, and `SLC-05`'s approval rule for changing them |
| [`MD-026`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md) | Reason codes behind every sanction and review-removal decision |
| `M12` §5.5, §5.6, §8.1 | The scorecard, the consequence ladder, the lifecycle |
| `M23` | Where sampled marketplace evidence becomes a nonconformity; the parity evidence for `G7-03` |
| [`SP-024`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-024_SOP_Marketplace_Seller_Onboarding_and_Governance.md) §5.3–§5.4, §7, §11 | The operator procedure, the authority limits and the SoD constraints this handbook promises |
| [`SP-028`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-028_SOP_Complaint_Escalation_and_Compensation.md), [`SP-029`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) | Customer complaint and nonconformity paths that run alongside a sanction |
| [`EO-001`](EO-001_Marketplace_Seller_Onboarding_Kit.md) | Introduces this handbook at stage 8; the seller acknowledges it before first award |
| [`EO-013`](EO-013_Ecosystem_Dispute_Resolution_Content.md) | Disputes — the input to the dispute-rate component and the appeal-adjacent process |
| [`EO-014`](EO-014_Ecosystem_Offboarding_and_Exit_Content.md) | What happens after removal, and reinstatement terms |
| [`UI-017`](../03_UI_Copy_and_Microcopy/03B_Portals/UI-017_P07_Marketplace_Seller_Portal_UI_Copy_Pack.md), [`UI-034`](../03_UI_Copy_and_Microcopy/03C_Admin_Workspaces/UI-034_Workspace_Marketplace_Console_Copy.md) | The seller's performance view and the operator console |
| [`NT-012`](../04_Notification_and_Messaging/04C_Email/NT-012_Email_Template_Library_Seller_and_Partner.md) | Every notice in §4.5 |
| [`TR-019`](../08_Training_and_Enablement/08B_Course_Packs/TR-019_Course_Pack_Marketplace_and_Seller_Operations.md) | The training a probation plan requires |

> **Rule-citation attribution.** **BRU-MKP-\***  → `M12` §9 — these are **module-scoped** rule families and **`05-05` carries none of them**. The families this file cites that **do** resolve in `05-05` are `BRU-ECM-*`. Stated per `AUDIT-015` R-11, which asked that the convention be recorded once rather than rediscovered by each extraction.

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Quarterly for the first four quarters after W7 launch — `MD-018` §6 requires threshold recalibration after the first quarter, and this handbook must move with it. Annually thereafter |
| Trigger for out-of-cycle review | Any change to a `MD-018` threshold; a change to the scorecard components in `M12`; an upheld appeal that reveals a measurement defect; a suspension challenged externally; a change to `LG-004` §4.8 or §4.9; a brand partner query about third-party work control |
| Owner | Marketplace Operations with the Quality Manager; **Legal Counsel approves every version** |
| Change control | **A version of this handbook is bound to the agreement version in force at the seller's signature.** A material change requires re-acceptance (`FR-MKP-009`) and notice; it is never applied retrospectively to a measured period (`SS-03`) |
| Effectiveness measure | Appeals upheld as a share of sanctions imposed — a high rate means the measurement is wrong, not that sellers are litigious |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The scorecard has no weights, no period and no minimum job count.** `FR-MKP-052` names seven components; nothing in the repository states how they combine, over what window, or how many jobs make a score stable. `MD-018` §6 concedes there is "no precedent — the marketplace does not exist yet". **§4.4 and §4.7 therefore describe a model with no parameters**, and `AUT-MKP-13` cannot be configured without them | CCO with Marketplace Operations and Quality Manager | **W7 — before the first automatic sanction** |
| **O-02** | **`LG-004` §4.8 is drafted *pending* its own open item, and this handbook is incorporated into it.** A Class B file whose contractual hook is provisional cannot reach `Approved`; `LG-001` records `LG-004` as awaiting gate `G5`. **Neither file can complete without the other**, and `AUDIT-013` recorded four upstream legal decisions blocking Category 10 | Legal Counsel | **W7 minus 10 working days** (`CG-007` G5 service level) |
| **O-03** | **The policy consequence of detected off-platform transacting is undecided** (`M12` Q-09: "warning, penalty, or removal"). §4.5.1 lists the breach and cannot state its consequence. Disintermediation is described in `M12` as *"the single largest commercial threat to a marketplace"* in a cash economy, and it is the one breach with no defined sanction | CCO | **W7 build** |
| **O-04** | **No appeal window or decision service level exists.** `FR-MKP-055` provides the appeal; `SOD-60` requires a second operator; `SP-024` §11 records that where none is available **"the appeal waits"** with no compensating control. A suspended seller earns nothing while it waits. **An unbounded appeal is a sanction with an unbounded duration**, which is the specific thing that makes an automatic-consequence regime challengeable | Legal Counsel with Marketplace Operations | **W7 — before launch** |
| **O-05** | **Second-operator availability is unresourced.** `SOD-60` and `SS-10` require an appeal decider who did not impose the sanction. At 500–2,000 sellers with a target dispute rate under 1.5% (`KPI-081`), the appeal volume is material and `M12` §13 names only *"Dispute Officer (new position under R24)"* — a single new position, which cannot satisfy the separation on its own | Programme Manager with CCO | **W7 — before launch** |
| **O-06** | **Bengali is required and unresourced.** This is a Class B instrument that a Bengali-reading seller must understand before it is applied to them. `CG-010` §4.1 makes English the governing text and requires a precedence clause drafted in `LG-001` and reproduced in each document — **which this file must carry and cannot until `LG-001`'s clause is settled** | Localisation Lead *(unappointed)* with Legal Counsel | **W7 minus 6 weeks** |
| **O-07** | **`G7-03` requires marketplace jobs to meet the same quality and evidence standards as owned jobs, and the parity evidence has no owner.** §4.3 makes the claim checkable; `M23` sampling (`SP-024` §5.3 step 13) is the mechanism; **no sampling rate, sample size or reporting cadence is defined anywhere**, and `M12` §14's "quality parity report" is a weekly dashboard with no specification | Quality Manager with BI Lead | **W7 — before the Gate 7 pack is assembled** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the three `EO` additions adapted to a standards handbook and the adaptation declared
- [x] Content class **B** assigned, with the `MD-018` `SLC-05` reasoning stated
- [x] The three conditions that make an automatic consequence defensible stated, and each mapped to where it is discharged
- [x] The standing journey rendered from `M12` §8.1, with restricted-per-category and suspended-per-seller distinguished
- [x] Twelve standards stated, with the enforcement mechanism for each
- [x] **Evidence checklist reproduced item by item, so the parity claim is falsifiable** (`G7-03`)
- [x] Scorecard components stated **with what each deliberately does not count**
- [x] Six-step sanction ladder, plus the six breaches that bypass it
- [x] Fifteen rules, ten of which constrain 1000FiX rather than the seller
- [x] Appeal route stated, including what an appeal cannot do, and the external route left explicitly open
- [x] Cold-start scoring problem addressed in the first-90-days section
- [x] All internal links resolve
- [x] Seven open items recorded
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` scorecard has no weights, period or minimum job count — outstanding; §4.4 has a model and no parameters**
- [ ] **`O-02` `LG-004` §4.8 provisional — outstanding; the contractual hook is not settled**
- [ ] **`O-03` off-platform consequence undecided — outstanding**
- [ ] **`O-04` no appeal window or service level — outstanding; an unbounded appeal is an unbounded sanction**
- [ ] **`G5` legal review not run** (`CG-007` §3.5) — required for Class B before `Approved`
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] `CG-010` §4.1 precedence clause reproduced from `LG-001` — **outstanding; clause not yet drafted**
- [ ] Named approver recorded — **pending Legal Counsel**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
