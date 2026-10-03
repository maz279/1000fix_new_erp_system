---
id: EO-003
title: Brand Partner Onboarding Pack
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Commercial
author: Commercial with Warranty and Content Design
reviewers: [Chief Commercial Officer, Finance Director, Warranty Officer, Quality Manager, Legal Counsel, Data Protection Officer, Content Design Lead]
approver: Content Design Lead with Commercial
content_class: D
purpose: >
  The pack issued to each of the 17+ authorised brand partners to move their warranty claim
  relationship from email and spreadsheet onto the P08 portal: what access they get, how a claim
  reaches them, what evidence arrives with it, how the reconciliation cycle works, and who to
  escalate to. The portal-claim target is more than 80% of claims against a base that is
  currently email; a brand that is not actively transitioned keeps emailing, and every brand
  still on email is a brand whose claims cannot be measured against the 45-day reimbursement
  target. Seventeen brands means seventeen transitions, not one launch.
traces_to: [P08, M09, M40, M23, M15, M17, M22, M24, M25, 04-00 P08, 04-00 PS-01, 04-00 PS-02, 05-04 §8 EA-01, EA-02, FR-WTY-052, FR-WTY-053, FR-WTY-054, FR-WTY-056, FR-WTY-057, FR-WTY-058, FR-WTY-059, FR-WTY-061, FR-PCM-013, FR-PCM-014, FR-PCM-015, FR-PCM-016, FR-PCM-017, FR-PCM-018, FR-PCM-019, FR-PCM-020, FR-PCM-021, BRU-PCM-07, BRU-PCM-08, BRU-PCM-20, KPI-037, KPI-039, KPI-040, KPI-041, KPI-063, G4-01, G4-02, MD-011, MD-017, MD-021, MD-029, LG-005, SP-014, UI-018, UI-033, HC-010, NT-013, DT-033, EO-004, EO-011, EO-012, EO-014, AP-007, CM-002, CM-015]
priority: P2
wave: W4
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P08 Brand Partner Portal capability set (claims, evidence, reconciliation, consignment parts, rate cards, performance, quality, certification, communication); KPIs "claims submitted through the portal (vs email) > 80%", "average claim decision time < 10 days", "claim approval rate > 92%", "days from service to reimbursement < 45"; 17+ brand partners, 50–150 users
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M40_Partner_Channel_Alliance_and_Franchise.md §3.1 items 4–5, §5.2 FR-PCM-013…021 authorisation register, expiry management, authorised technician register, audit calendar, obligation tracking, health score, engagement log, performance exchange; §9 BRU-PCM-07, BRU-PCM-08, BRU-PCM-20; §18 Q-01
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M09_Warranty_Protection_Plans_and_Claims.md §5.5 FR-WTY-052…061 claim receivable, remittance matching, period reconciliation, write-off governance, consignment parts, defective part return, old-part retention, recall and campaign execution, brand partner performance
    verified: 2026-08-18
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md §2 record structure — agreement_ref, authorised_categories, claim_submission_channel, claim_window_days, rate_card_owner, consignment_parts, requires_certified_tech, reimbursement_days_target; §4 BRD-01…BRD-07
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §2.5 KPI-037, KPI-039, KPI-040, KPI-041; §2.8 KPI-063; §4 Gate 4 G4-01, G4-02
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Brand Partner Onboarding Pack

| Item | Value |
|---|---|
| Audience | Authorised brand partners — warranty, technical and finance contacts |
| Population | **17+ brands**, 50–150 named users (`04-00` P08) |
| Portal | `P08` Brand Partner Portal |
| Language | **English only** (`CG-010` §3.2 — brand partners are international counterparties) |
| Issued by | Commercial, per brand, as a transition rather than a launch |
| Wave | W4 · Months 14–18 (`06-01` §3) |
| Gate criteria evidenced | `G4-01` claims auto-created within 24 h and submitted within 72 · `G4-02` first-submission approval ≥ 90% |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3), all
> six sections in order. The three `EO` additions appear as §4.1 (**onboarding journey** — the
> per-brand transition), §4.3 (**checklist** — what each side must supply before a brand can be
> switched on) and §4.7 (**first 90 days** — the parallel-running period). Template 15
> `TPL_Onboarding_Kit.md` does not exist; see the category audit.

---

## 1. Purpose

The 17+ brand authorisations are not a partner programme. `M40` §2 states what they actually are:
*"the foundation of the entire business"* — the basis on which 1000FiX may perform warranty work
at all, and the asset that `M12`'s risk register protects when it rates marketplace quality
failure as Critical.

`04-00` sets P08's transition target at **more than 80% of claims submitted through the portal
rather than by email**. That number is not a systems metric. Every brand currently submits claims
the way it has always submitted them, through a person who has always received them, and no
portal moves a working email relationship on its own.

Three failures follow from onboarding brands without a pack:

| Absent | Consequence |
|---|---|
| A stated per-brand transition | Brands adopt at seventeen different speeds and none of them is measured. `KPI-040`'s 45-day reimbursement target cannot be computed on a base that is half email |
| A stated evidence expectation **before** the first portal claim | The first portal claim is rejected, and the brand concludes the portal is the reason. `KPI-039` targets 90% first-submission approval at W4 |
| Named escalation contacts on both sides | A stuck claim escalates through whoever answers, which for a brand relationship is the account manager and for 1000FiX is the Finance Director |

**What this pack is not.** It is not the portal terms (`LG-005`), not the claim rules and evidence
standard (`EO-004`), not the screen copy (`UI-018`), not the help set (`HC-010`), and not the
internal claim procedure (`SP-014`). It is the **transition artefact** — the document a Commercial
lead takes into a meeting with one brand, to move that brand.

---

## 2. Scope

**In scope.** Portal access and user roles for a brand; what a brand can and cannot see; the claim
lifecycle as the brand experiences it; the evidence pack that arrives with a claim; decision
options and their consequences; the reconciliation and remittance cycle; consignment parts,
defective returns and old-part retention where they apply; performance and quality exchange in
both directions; bulletins, technical notices and recalls; the escalation ladder with named roles;
and the per-brand transition and parallel-running plan.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| The portal terms of use and the confidentiality position | `LG-005` |
| Per-brand claim rules, required evidence and rejection reasons | **`EO-004`** — this pack points at it; `EO-004` states it |
| The brand master record and its fields | `MD-017`; certifications `MD-011`; device families `MD-021` |
| Reimbursement rates and rate cards | `MD-029`; changes communicated under `EO-011` |
| The internal claim submission and reconciliation procedure | `SP-014` |
| Portal screen copy; the internal warranty console | `UI-018`; `UI-033` |
| Help articles | `HC-010` |
| Claim notifications and bulletins | `NT-013` |
| The claim submission document itself | `DT-033` |
| Co-branding and use of brand marks | **`EO-012`** |
| Authorisation lapse, relationship exit and its consequences | **`EO-014`** |
| The brand's own warranty system integrating to ours by API | **`AP-007`** Partner Integration Guide — Brands |
| Programme-level stakeholder communication about the change | `CM-002`, `CM-015` |

> **The `AP-007` boundary matters at stage 3.** A brand with its own warranty system may not want a
> portal at all; `AP-007` documents the API path and this pack documents the portal path.
> **Stage 1 must establish which of the two a brand is taking**, because the §4.7 parallel run and
> the `MD-017` `claim_submission_channel` value differ — `portal` against `api` — and a brand
> transitioned to the wrong one is transitioned twice.

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Brand warranty manager** | The claim lifecycle, decision options, and what evidence to expect |
| **Brand finance contact** | The reconciliation cycle, remittance matching and short-payment resolution |
| **Brand technical contact** | Bulletins, technical notices, recalls, and the certified-technician register |
| **Brand regional or country manager** | The performance exchange and the escalation ladder |
| **1000FiX Commercial lead** | The pack they present, brand by brand |
| **1000FiX Warranty Officer (`R28`)** | What has been promised to the brand about turnaround and evidence |
| **Finance Director** | The reconciliation commitments and the write-off governance boundary |

---

## 4. Content

### 4.1 The per-brand transition journey

**Seventeen transitions, not one launch.** Each brand runs this sequence independently, and the
`04-00` 80% target is the weighted result of seventeen of them.

| # | Stage | 1000FiX does | The brand does | Exit condition |
|---|---|---|---|---|
| **1** | **Relationship confirmation** | Confirms the authorisation record — scope, territory, expiry, conditions — against the authorising document | Confirms the record is current | `MD-017` `agreement_ref` resolves in `M24` (`BRD-01`) |
| **2** | **Contact mapping** | Records named warranty, technical, finance and escalation contacts with their portal scope | Names them, with deputies | Every role filled; no shared mailboxes |
| **3** | **Rules capture** | Captures the brand's claim rules, evidence requirements, claim window and rate-card ownership | Confirms or corrects them | Rules recorded in **`EO-004`** for that brand |
| **4** | **Access provisioning** | Provisions `P08` accounts through `M29` under `PS-01` single sign-on | Accepts `LG-005`; completes access setup | Users can sign in and see **only their own brand** (`EA-01`, `EA-02`) |
| **5** | **Walkthrough** | Demonstrates a real claim end to end, with a real evidence pack | Attends with the people who will decide claims | The brand's decider has decided one claim in the portal |
| **6** | **Parallel run** | Submits through the portal **and** the existing channel | Decides through both; compares | §4.7 |
| **7** | **Cutover** | Switches `MD-017` `claim_submission_channel` to `portal` | Stops accepting the old channel | First full period with no email claims |
| **8** | **First reconciliation** | Runs the period reconciliation and issues the signed statement (`FR-WTY-054`) | Uploads remittance advice; resolves differences | Statement agreed |
| **9** | **Steady state** | Performance exchange, audit calendar, obligation tracking | Publishes rate-card and rule changes through the portal | `KPI-040` measurable for this brand |

> **Stage 7 is the only stage that moves the KPI, and stage 6 is the only stage that makes stage 7
> safe.** A cutover without a parallel run is how a brand's first bad month becomes an argument
> about the portal rather than about the claims.

### 4.2 What a brand partner can see — and cannot

Stated early and plainly, because it is the first question a brand asks and the answer is a
selling point.

| Can see | Cannot see |
|---|---|
| Claims submitted **against their own brand**, with the full evidence pack | Any other brand's claims, volumes or performance |
| Photographs, diagnostic reports, parts replaced, technician certification, purchase proof | 1000FiX cost, margin, or labour rates other than their own agreed rates |
| Their own consignment stock position, consumption and replenishment | 1000FiX-owned stock or network inventory |
| 1000FiX service performance **on their brand** — volume, TAT, first-time fix, rework, CSAT, failure patterns by model | Customer personal data beyond what a claim requires |
| The certification status of technicians authorised **on their brand** | The employment records behind those certifications |
| Their own rate cards and claim rules | Any other brand's commercial terms |

`EA-01` and `EA-02` enforce this at the record-rule layer; `LG-005` §4.2 states it as the "hard
boundary". **A brand that suspects it can see a competitor's data will not use the portal**, and
this table is the answer given before the suspicion forms.

### 4.3 The onboarding checklist

Two columns, because a transition that only asks things of the brand stalls at stage 3.

#### What 1000FiX must have before a brand can be switched on

| # | Item | Source | Blocking |
|---|---|---|---|
| 1 | Current authorisation document, resolving in `M24` | `MD-017` `agreement_ref`, `BRD-01` | **Yes — no agreement, no authorisation** |
| 2 | Authorised categories, and models where narrower | `MD-017` `authorised_categories`, `authorised_models` | **Yes** (`BRD-04`) |
| 3 | Agreement effective and expiry dates | `MD-017` `agreement_from` / `agreement_to` | **Yes** (`BRD-02`) |
| 4 | Claim window in days from service | `MD-017` `claim_window_days` | **Yes** |
| 5 | Rate-card ownership — brand, 1000FiX or negotiated — and the rate card | `MD-017` `rate_card_owner`, `rate_card_code` → `MD-029` | **Yes** |
| 6 | Whether certified technicians are required | `MD-017` `requires_certified_tech` → `BRU-SRM-09` | **Yes** |
| 7 | Consignment parts flag and, where true, the consignment terms | `MD-017` `consignment_parts`; terms in `M42` `FR-SRM2-024` | Conditional |
| 8 | Reimbursement days target | `MD-017` `reimbursement_days_target` | **Yes** — `KPI-040` is measured against it |
| 9 | Named primary contact | `MD-017` `primary_contact_name` | **Yes** |
| 10 | Per-brand claim rules and evidence requirements | **`EO-004`** | **Yes** — a claim cannot be assembled without them |

#### What the brand must supply or confirm

| # | Item | Why | Blocking |
|---|---|---|---|
| 11 | Named users with roles — warranty decision, technical, finance, escalation | Portal scope is per user, not per organisation | **Yes** |
| 12 | Acceptance of `LG-005` portal terms | Access precondition | **Yes** |
| 13 | Decision-authority limits per user | So a claim is not routed to someone who cannot decide it | **Yes** |
| 14 | The rejection reasons the brand actually uses | They become the reason set in `EO-004` and `MD-026` | **Yes** |
| 15 | Remittance advice format and cycle | Drives `FR-WTY-053` matching | **Yes** |
| 16 | Defective-part return requirement and destination | `FR-WTY-057`; affects claim payability | Conditional |
| 17 | Old-part retention and destruction rules | `FR-WTY-058` | Conditional |
| 18 | Technical notice, bulletin and recall channel | `FR-WTY-059`, P08 communication | No — but a recall with no channel is a safety exposure |
| 19 | Audit calendar and scope | `FR-PCM-016`; `P11` conducts them | No |
| 20 | Obligations under the authorisation — tooling, training, facility, reporting, stock holding | `FR-PCM-017`; tracked with evidence and due dates | **Yes for the record**, not for access |

### 4.4 The claim, as the brand experiences it

`SP-014` owns the internal procedure; this is the brand-side view, and the two must not diverge.

| Step | What happens | Timing | Rule |
|---|---|---|---|
| Service completed under warranty | The claim is created automatically | **Within 24 hours** | `G4-01` |
| Claim assembled | Evidence pack attached per the brand's `EO-004` rules | — | `KPI-041` targets 96% complete at W4, 98% at W8 |
| Certified-technician check | Blocked if the brand requires certification the technician lacks | Before submission | `BRU-SRM-09`; `KPI-063` targets **zero** claims rejected for this reason |
| Submitted | Reaches the brand in `P08` | **Within 72 hours of service** | `G4-01`, `KPI-037` |
| Brand decides | Approve, part-approve, reject with reason, or request more information; bulk actions available | **Target < 10 days** (`04-00` P08) | — |
| Approved | Claim receivable raised at the approved value | On approval | `FR-WTY-052` |
| Paid | Remittance advice uploaded and matched | — | `FR-WTY-053` |
| Reconciled | Period statement per brand: claimed, approved, rejected, paid, outstanding | Per period | `FR-WTY-054` |

**Part-approval and "more information" are first-class outcomes, not failures.** A brand that
part-approves has told 1000FiX something precise; a brand that rejects wholesale has told it
nothing. `EO-004` exists to turn the second into the first, and `KPI-039`'s 90% first-submission
approval target is only reachable if brands use the finer-grained outcomes.

### 4.5 Reconciliation, and what happens when the numbers differ

| Situation | What 1000FiX does | What the brand does |
|---|---|---|
| Remittance matches the approved claims | Closes the period | — |
| **Short payment** | Identifies the shortfall per claim and raises it (`FR-WTY-053`) | States the reason per claim, not per remittance |
| Unmatched item on the remittance | Holds it in an unmatched register and resolves it | Supplies the claim reference |
| Claim approved and never paid | Ages it and escalates on the §4.6 ladder | Confirms the payment run it falls in |
| Claim unrecoverable | **Write-off requires approval, with segregation between the raiser and the approver** (`FR-WTY-055`) | Informed; the write-off is not a concession of the underlying claim |

> **Write-off governance is stated to the brand deliberately.** It tells a brand that an aged
> claim does not quietly disappear on the 1000FiX side, which is the assumption that makes a
> finance contact stop responding.

### 4.6 Escalation — named roles, both directions

| Level | 1000FiX | Brand | Trigger | Timebox |
|---|---|---|---|---|
| 1 | Warranty Officer (`R28`) | Warranty contact | A claim stuck beyond the decision target | 3 working days |
| 2 | Warranty Manager / Commercial lead | Regional warranty manager | A pattern across claims; a rejection-reason dispute | 5 working days |
| 3 | **Finance Director** *(the `MD-017` and `BRU-PCM-07` owner)* | Country or regional manager | Reconciliation dispute; reimbursement ageing beyond target | 10 working days |
| 4 | **CCO, then CEO** | Brand principal | Authorisation at risk; `FR-PCM-019` at-risk detection fired | Immediate |
| — | Quality Manager (`R32`) ↔ brand quality | Both directions | Quality concern, CAPA, recall, counterfeit finding | Per `M23` |

**`FR-PCM-018` computes a relationship health score** from claim performance, quality, audit
findings, obligation compliance, volume trend and contact engagement, and `BRU-PCM-18` requires it
to decompose into its named factors. The brand is shown the factors that concern them.
**`BRU-PCM-20` requires the brand's own assessment of 1000FiX to be recorded verbatim and to be
uneditable by the account owner** — the pack says so, because a feedback channel a partner
believes is filtered is a feedback channel they stop using.

### 4.7 The first 90 days — the parallel run

| Days | 1000FiX | Brand | Decision point |
|---|---|---|---|
| **0–30** | Every claim submitted through **both** the portal and the existing channel | Decides through both; flags any difference in what arrives | Are the portal evidence packs complete and legible? |
| **31–60** | Portal becomes primary; email accepted but reconciled against the portal | Decides in the portal; uses email only by exception | First-submission approval rate for this brand, measured |
| **61–90** | Email closed for this brand; `MD-017` `claim_submission_channel` set to `portal` | Confirms cutover in writing | **Cutover decision.** Do not cut over on a rate below the brand's own pre-portal baseline |
| **91+** | First full-period reconciliation and signed statement | Remittance uploaded to the portal | Steady state; this brand now contributes to `KPI-040` |

**The cutover criterion is comparative, not absolute.** A brand whose first-submission approval
rate on the portal is *below its own email baseline* has a rules or evidence problem in `EO-004`,
and cutting over converts a content defect into a commercial dispute.

**Recall readiness is part of the first 90 days, not a later phase.** `FR-WTY-059` executes a
recall as a batch of service orders against affected serial ranges. A brand that has not tested
the notice channel during the parallel run will test it during a recall, and a recall is the one
brand communication with a safety consequence.

### 4.8 Rules

| # | Rule |
|---|---|
| **BO-01** | The pack is issued **per brand**, populated from that brand's `MD-017` record. There is no generic edition |
| **BO-02** | No claim rule, evidence requirement or rejection reason is stated here. **`EO-004` owns them**, per brand |
| **BO-03** | No rate, reimbursement value or commercial term is stated here. `MD-029` owns them; `EO-011` governs how changes are communicated |
| **BO-04** | The data-boundary table (§4.2) appears in every edition, unabridged |
| **BO-05** | Every contact is a named person with a named deputy. **Shared mailboxes are not accepted on either side** — an escalation ladder with a mailbox at level 3 has no level 3 |
| **BO-06** | Cutover is a decision against the §4.7 criterion, never a date |
| **BO-07** | The pack states 1000FiX's obligations to the brand as clearly as the brand's to 1000FiX — decision targets, evidence completeness, reconciliation cadence |
| **BO-08** | Authorisation expiry is described as a **hard consequence**: work requiring an authorisation cannot be performed once it has lapsed (`BRU-PCM-08`), and an authorisation may never lapse without escalation having fired (`BRU-PCM-07`) |
| **BO-09** | The certified-technician requirement is stated where `requires_certified_tech` is true, with `KPI-063`'s zero target named |
| **BO-10** | The brand's verbatim assessment channel is described, with the uneditability rule (`BRU-PCM-20`) |
| **BO-11** | English only (`CG-010` §3.2). Where a brand's local entity works in Bengali, that is handled by a named bilingual contact, **not by translating this pack** — `O-05` |
| **BO-12** | Nothing in this pack varies `LG-005`. A brand asking for a variation is routed to Legal, not accommodated in the pack |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`MD-017`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md) | Every field the pack is populated from; `BRD-01`…`BRD-07` are the checks it depends on |
| [`EO-004`](EO-004_Brand_Claim_Rules_and_Evidence_Standard_Guide.md) | The per-brand claim rules and evidence standard — **stage 3 cannot exit without it** |
| [`LG-005`](../10_Legal_Policy_and_Compliance/LG-005_Brand_Partner_Portal_Terms.md) | Portal terms accepted at stage 4 |
| `M09` §5.5 | Claim receivable, remittance matching, reconciliation, write-off, consignment, defective return, recall |
| `M40` §5.2 | The authorisation register, expiry management, audit calendar, obligation tracking and health score this pack describes |
| `M23` | Quality concerns, CAPA and partner audits |
| `M22`, [`MD-011`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md) | The certified-technician register the brand sees |
| [`SP-014`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md) | The internal procedure this pack must not contradict |
| [`UI-018`](../03_UI_Copy_and_Microcopy/03B_Portals/UI-018_P08_Brand_Partner_Portal_UI_Copy_Pack.md), [`HC-010`](../09_Help_Centre_and_Self_Service/09A_Help_Sets_By_Portal/HC-010_Help_Set_P08_Brand_Partner_Portal.md), [`NT-013`](../04_Notification_and_Messaging/04C_Email/NT-013_Email_Template_Library_Brand_Partner_Claims.md), `DT-033` | Screens, help, notices and the claim document |
| [`MD-029`](../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-029_Price_List_and_Rate_Card_Seed.md) | Rate cards; `EO-011` for change communication |
| [`EO-012`](EO-012_Co_Marketing_and_Co_Branding_Asset_Guide.md) | Use of the brand's marks, and of ours |
| [`EO-014`](EO-014_Ecosystem_Offboarding_and_Exit_Content.md) | Authorisation lapse and relationship exit |

> **Rule-citation attribution.** **BRU-PCM-\***  → `M40` §9 — these are **module-scoped** rule families and **`05-05` carries none of them**. The families this file cites that **do** resolve in `05-05` are `BRU-SRM-*`. Stated per `AUDIT-015` R-11, which asked that the convention be recorded once rather than rediscovered by each extraction.

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per brand at each authorisation renewal; the master pack annually |
| Trigger for out-of-cycle review | An authorisation scope or expiry change; a change to the brand's claim rules or rate card; a `P08` release changing the claim flow; a recall; `FR-PCM-019` at-risk detection firing; a change to `LG-005` |
| Owner | Commercial, with the Warranty Officer for §4.4–§4.5 |
| Change control | A change affecting what a brand is told about decision targets or reconciliation requires Finance Director sign-off, because those are the commitments a brand will hold 1000FiX to |
| Effectiveness measure | Portal claim share per brand against the `04-00` 80% target, and first-submission approval rate per brand against `KPI-039` |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **This pack is W4 and `M40` — the module that owns the brand relationship — is W7.** `M40` §5.2 holds the authorisation register, expiry management, obligation tracking, audit calendar, health score and at-risk detection that §4.3 and §4.6 depend on. `02-02` §wave places `M40` at W7 (Months 27–30); `P08` and `M09` are W4 (Months 14–18). **`M40` Q-01 asks this exact question** — *"should the brand-authorisation register be advanced to W4 alongside M09, given that it protects revenue streams 1 and 4 from day one?"* — and answers it *"W3 — roadmap decision"*. **Until it is answered, §4.3 items 1–3 and 20 and the whole of §4.6's health-score paragraph describe capability that does not exist at the wave this pack is issued** | **CTO / CCO / Programme Board** | **W3 — roadmap decision, per `M40` Q-01** |
| **O-02** | **`04-00`'s four P08 targets have no registered KPI identifier.** Portal claim share > 80%, decision time < 10 days, approval rate > 92% and brand satisfaction > 4.5 appear only in the portal specification. `06-02` §2.5 registers `KPI-037`, `KPI-039`, `KPI-040` and `KPI-041`, and **none of them is the portal-adoption figure this pack exists to move.** A target with no registered identifier is not measured at a gate. **This is an instance of `AUDIT-015` RP-01, not a new finding**: that audit counted **250 KPI identifiers in use against 95 registered in `06-02`**, with 196 unregistered, and recommended widening the register per `RP-001` §4.3 (R-01). These four P08 targets are part of the 196 | BI Lead with Enterprise Architecture | **W4 — before the Gate 4 pack** |
| **O-03** | **`KPI-039` and `04-00` state different approval-rate targets** — 90% at W4 / 92% at W8 in `06-02`, against *"claim approval rate > 92%"* in `04-00` with no wave. §4.4 quotes both and cannot reconcile them. The Master Index's `EO-004` row quotes *"> 92%"* as the governing figure | Enterprise Architecture with Finance Director | W4 |
| **O-04** | **Consignment terms are owned by `M42` (`FR-SRM2-024`) and `M42` is W4, but no `EO` or `MD` file holds the brand-side consignment content.** §4.3 item 7 and the P08 "consignment parts" capability require terms — parts in scope, holding locations, valuation basis, settlement trigger, return rights, reconciliation frequency, liability for loss — and `MD-017` carries only a boolean flag. **Seven brands with consignment stock would be seven undocumented stock liabilities** | Supply Chain Director with Warranty Officer | **W4 — before the first consignment brand is switched on** |
| **O-05** | **`BO-11` states an English-only position that `CG-010` §3.2's rationale supports and the field may not.** Several of the 17+ brands operate through Bangladeshi distributors and local service arms whose warranty staff read Bengali. The rule routes this to "a named bilingual contact", which is a mitigation, not a decision. **No brand-by-brand language audit has been done** | Commercial with Localisation Lead | W4 |
| **O-06** | **No parallel-run capacity is allocated.** §4.7 requires every claim submitted twice for 30 days, per brand, across 17+ brands with staggered starts. `06-01` §3 Wave 4 lists no line for it, and the Warranty Officer role (`R28`, 4–10 people) is the same team running the live claim pipeline against `KPI-038`'s warranty-leakage target | Programme Manager with Finance Director | **W4 — before the first transition** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the three `EO` additions placed and the template gap noted
- [x] Nine-stage per-brand transition journey with an exit condition at every stage
- [x] **Seventeen transitions framed as seventeen, not as one launch**
- [x] Data-boundary table stated in both directions, with the `EA-01`/`EA-02` enforcement named
- [x] Checklist split into what 1000FiX must have and what the brand must supply, each item traced to its owning field or rule
- [x] Claim lifecycle stated from the brand's side, reconciled against `SP-014`'s internal view
- [x] Reconciliation section covers short payment, unmatched items, ageing and write-off governance
- [x] Escalation ladder with named roles and timeboxes on both sides, to CEO / brand principal
- [x] **`BRU-PCM-20`'s verbatim, uneditable brand assessment stated to the brand**
- [x] First-90-days parallel run with a **comparative** cutover criterion rather than a date
- [x] Twelve rules, including the prohibition on stating claim rules, rates or `LG-005` variations
- [x] All internal links resolve
- [x] Six open items recorded
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` `M40` is W7 and this pack is W4 — outstanding; a roadmap decision `M40` Q-01 already asked for**
- [ ] **`O-02` the target this pack exists to move has no registered KPI — outstanding**
- [ ] **`O-04` brand consignment terms have no owning content file — outstanding**
- [ ] **`O-06` parallel-run capacity unallocated — outstanding**
- [ ] Per-brand editions populated from `MD-017` — **outstanding; `MD-017` holds 0 rows until brand data is loaded**
- [ ] Named approver recorded — **pending Content Design Lead with Commercial**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2, subject to `O-05`

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
