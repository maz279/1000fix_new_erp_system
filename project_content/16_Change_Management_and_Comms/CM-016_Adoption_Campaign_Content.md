---
id: CM-016
title: Adoption Campaign Content
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Marketing with Change
author: Marketing Manager with the Change Lead and Content Design
reviewers: [CCO, CEO, Marketing Manager, Operations Director, Account Management Lead, Marketplace Operations, Legal & Compliance, Localisation Lead, Content Design Lead, Support Lead, Programme Content Lead]
approver: Content Design Lead, with Legal approving consent basis and the CCO approving external targets
content_class: D
purpose: >
  Supplies the campaign content that moves each portal from available to used, against the
  adoption targets those portals were specified with — P01 at 88% online booking, P04 at 85% of
  contracted clients, P05 at 90% PO acknowledgement, P08 at 80% portal claims — and states the
  rule that a target missed is a product or process finding before it is a campaign one. Adoption
  is marketed, not assumed; a portal that is merely available reaches the people who were going to
  find it anyway.
traces_to: [04-00, 06-02, P01, P04, P05, P07, P08, P12, CM-001, CM-002, CM-004, CM-007, CM-013, CM-014, CM-015, CM-017, MD-021, LG-008, NT-001, HC-016, RP-001]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: CM-016_Adoption_Campaign_Content_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P01…§P12 KPI tables — the adoption targets each portal was specified against
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §1 — every portal is measured; adoption, task completion and error rates are KPIs, not afterthoughts
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §5.5 — adoption report to the Steering Committee monthly during rollout, usage by role and branch, with intervention where lagging
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §1.2 RSK-010, RSK-011, RSK-012 — marketplace sellers, corporate clients and management adoption risks with their mitigations
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 §4 — gate criteria that are themselves adoption measures, including G2-01, G2-08, G4-05 and G7-01
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §1.4a RSK-032 — Personal Data Protection Act 2026; marketing communication requires a lawful basis and a valid consent state
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# CM-016 — Adoption Campaign Content

> **Scope note.** This file owns **campaign content and the adoption measurement that directs
> it**. It does not own the transition messages that precede a campaign (`CM-013`, `CM-014`,
> `CM-015`), the recognition copy a campaign may use (`CM-017`), in-product help or onboarding
> tours (`HC-016`), or any portal's design.
>
> **Discipline note.** `UP-03` is the rule this file exists to protect: **a missed adoption target
> is investigated as a product or process problem before a campaign is commissioned.** Campaigning
> at a broken funnel spends money to send more people into it.

---

## 1. Purpose

The register's justification is exact: *"`P01` targets 88% online booking and `P04` targets 85%
active corporate clients. Adoption is marketed, not assumed."*

`04-00` §1 makes the same point structurally: *"every portal is measured — adoption, task
completion and error rates are KPIs, not afterthoughts."* Six of the nine wave gates contain a
criterion that is an adoption measure rather than a delivery measure. A portal that works and is
not used fails its gate exactly as a portal that does not work.

**Consequence of absence (`CP-03`).**

| Failure | Consequence |
|---|---|
| No campaign | The portal reaches the people who would have found it anyway; the target is missed by a margin nobody planned for |
| No measurement | Intervention is not possible because lagging is not visible until the gate |
| Campaigning before the funnel is fixed | Money spent driving traffic into a step where users abandon |
| No consent discipline | A marketing campaign to 250,000+ people on an unconfirmed basis (`RSK-032`) |
| One campaign for all portals | Six external populations with different motivations receive the same argument |
| Internal adoption treated as marketing | Staff campaigned at rather than supported (`OJ-16`) |
| No baseline | *"Adoption is up"* with nothing to be up from |
| Campaign continues after the target is met | Spend continues and message fatigue sets in |

---

## 2. Scope

**In scope:** the adoption target register; the measurement model and its baseline rule; the
diagnose-before-campaign rule; campaign content per audience; the internal-adoption distinction;
consent and channel rules; the intervention ladder; stop conditions; and rules `UP-01`…`UP-17`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Transition messages | [`CM-013_Customer_Migration_and_Transition_Pack.md`](CM-013_Customer_Migration_and_Transition_Pack.md), [`CM-014_Corporate_Client_Transition_Pack.md`](CM-014_Corporate_Client_Transition_Pack.md), [`CM-015_Vendor_and_Seller_Transition_Pack.md`](CM-015_Vendor_and_Seller_Transition_Pack.md) |
| Recognition, leaderboard and milestone copy | [`CM-017_Recognition_Incentive_and_Gamification_Copy.md`](CM-017_Recognition_Incentive_and_Gamification_Copy.md) |
| In-product tours, coach marks and empty states | `HC-016`; `UI-006` |
| Onboarding kits for external audiences | Category 18 `EO` — [`EO-001`](../18_Ecosystem_Onboarding_Content/EO-001_Marketplace_Seller_Onboarding_Kit.md), [`EO-005`](../18_Ecosystem_Onboarding_Content/EO-005_Vendor_and_Supplier_Onboarding_Pack.md), [`EO-007`](../18_Ecosystem_Onboarding_Content/EO-007_Corporate_Client_Onboarding_and_Welcome_Kit.md) |
| Metric definitions, dashboards and the semantic layer | [`RP-001`](../14_Reporting_Analytics_and_KPI/RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md), [`RP-006`](../14_Reporting_Analytics_and_KPI/RP-006_BI_Semantic_Layer_Data_Dictionary.md); baselines in [`RP-015`](../14_Reporting_Analytics_and_KPI/RP-015_Benefits_Realisation_and_KPI_Baseline_Register.md) |
| Portal design, funnel design and UX | `04-00`; the portal squads |
| Consent capture and privacy notice | `LG-008`; `MD-021` consent state |
| Market-facing brand advertising | The corporate website content set — separate register |
| Commission, pricing or fee incentives to drive adoption | Commercial; `M11`, `M12`, `M40` |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Marketing Manager (`R23`)** | Run campaigns against stated targets with a stop condition |
| **Change Lead** | Report adoption to Steering and trigger intervention |
| **Account managers (`R22`)** | Drive `P04` adoption per account rather than by broadcast |
| **Marketplace Operations (`R24`)** | Drive `P07` seller activity against `RSK-010` |
| **Procurement (`R19`)** | Drive `P05` vendor adoption |
| **Portal squads** | Receive the funnel finding before the campaign |
| **Steering Committee (`S02`)** | See the worst-performing audience monthly |

---

## 4. Content

### 4.1 The adoption target register

**`UP-01`: every target is quoted from `04-00` or `06-02`, never invented.** Nine targets carry a
gate criterion; those are the ones a campaign cannot be optional for.

| Portal / audience | Target | Baseline | Source | Gate criterion |
|---|---|---|---|:--:|
| **`P01` Customer** | **Online booking 88%** | **40%** | `04-00` §P01 | `G2-08` (≥ 60% at pilot) |
| `P01` Customer | Self-service status checks > 80% of enquiries | ~0 | `04-00` §P01 | — |
| `P01` Customer | Portal MAU > 120,000 | — | `04-00` §P01 | — |
| **`P02` Technician** | **Daily active use > 95% of active technicians** | 0 | `04-00` §P02 | **`G2-01` 100% of Dhaka technicians** |
| `P03` Admin | Training time to competence < 4 hours | — | `04-00` §P03 | `G1-11` |
| **`P04` Corporate** | **> 85% of contracted clients active** | 0 | `04-00` §P04 | **`G4-05` 10+ clients transacting** |
| `P04` Corporate | > 70% of corporate requests via portal | 0 | `04-00` §P04 | — |
| **`P05` Vendor** | **> 90% POs acknowledged in portal** | 0 | `04-00` §P05 | — |
| `P05` Vendor | > 85% invoices via portal; RFQ response > 75% | 0 | `04-00` §P05 | — |
| `P06` Analytics | Weekly manager usage > 90% | 0 | `04-00` §P06 | `G4-09`; `RSK-012` |
| **`P07` Seller** | **Onboarding completion > 60% of started registrations** | — | `04-00` §P07 | **`G7-01` 200+ transacting** |
| `P07` Seller | Monthly active > 70% of approved sellers | — | `04-00` §P07 | — |
| **`P08` Brand** | **> 80% of claims via portal, not email** | 0 | `04-00` §P08 | — |
| `P09` Rider | POD capture completeness 100% | — | `04-00` §P09 | — |
| `P10` Contact centre | Disposition coding completeness 100% | — | `04-00` §P10 | `G4-06` |
| `P11` Auditor | Audits on mobile 100%, vs paper | 0 | `04-00` §P11 | `G5-04` |
| **`P12` Partner** | **Portal adoption > 75% of approved partners** | — | `04-00` §P12 | — |
| `P12` Partner | Referral-attributed new customers > 12% | — | `04-00` §P12 | — |

> **`UP-02` — a target with no baseline cannot be campaigned against.** Ten of the eighteen rows
> above have no baseline value in the specification. `00-04` §8 names *"benefits are never
> measured"* as a programme failure mode and gives the mechanism: baselines captured **before**
> each wave. Recorded as `O-01`.

### 4.2 Diagnose before campaigning

**`UP-03`: a missed target is diagnosed before a campaign is commissioned.** The diagnostic order
is fixed:

| # | Question | If yes | Owner |
|:--:|---|---|---|
| 1 | **Can they reach it?** Access, device, connectivity, literacy | Fix access. Not a campaign | IT / Ops |
| 2 | **Do they know it exists?** | **Campaign** — this is the awareness case | Marketing |
| 3 | **Can they complete it?** Funnel completion by step | **Product finding** → portal squad. Not a campaign | Portal squad |
| 4 | **Is it faster than what they do now?** | **Process or design finding.** Campaigning against a slower alternative fails | Business Process |
| 5 | **Are they worse off if they use it?** | **`Interest` objection** (`OJ-02`) → escalate | Change Lead → Steering |
| 6 | **Is someone telling them not to?** | Management or intermediary issue | Operations / Commercial |

> **`UP-04` — only question 2 is answered by a campaign.** `P01`'s primary design KPI is booking
> funnel conversion at > 72%; if conversion is below that, more traffic increases abandonment and
> nothing else.

### 4.3 Measurement

| Element | Rule |
|---|---|
| **Baseline** | Captured **before the wave**, with the date (`EP-11`) |
| **Grain** | By **role and branch** for internal, by **segment and cohort** for external (`00-04` §5.5) |
| Cadence | **Weekly during rollout**, monthly thereafter |
| Reporting | `CM-004` Section 5, **worst performer first** (`EP-06`) |
| **Denominator** | Stated with every figure, always (`NL-07`, `EP-05`) |
| Active definition | Defined once per portal, published, and **not changed to flatter a number** |
| Attribution | A campaign claims a change only against a pre-campaign trend, never against zero |
| Source | The product's own instrumentation (`PS-10`), not a survey |

> **`UP-05` — "active" is defined once and published.** The single easiest way to meet an adoption
> target is to redefine active. The definition is recorded in `RF-006` and a change to it is a
> decision, not an adjustment.

### 4.4 Campaign content by audience

**`UP-06`: each audience is campaigned on its own reason, and the reason is a benefit to them,
not to the company.**

| Audience | The reason that works | The reason that does not | Channel | Language |
|---|---|---|---|---|
| **`P01` Customers** | *"Book in three steps and see where your technician is, without calling."* | *"Reduce our call volume"* | In-app, SMS to consenting, portal, hotline IVR, counter card | **BN-first** |
| **`P02` Technicians** | *"Your earnings and your jobs, on your phone, with no signal needed."* | *"Compliance with recording requirements"* | **Champion, supervisor, toolbox talk** — not a campaign channel | **BN only** |
| **`P04` Corporate** | *"Raise 50 requests in five minutes and see your estate's SLA position."* | *"We prefer portal submissions"* | **Account manager, 1:1** | EN |
| **`P05` Vendors** | *"See your payment schedule and your PO status without phoning."* | *"Reduce vendor queries by 60%"* | Procurement officer + portal | EN |
| **`P07` Sellers** | *"Faster payouts and jobs matched to what you do."* | *"Platform standards compliance"* | In-app, seller comms, cohort onboarding | **BN-first** |
| **`P08` Brands** | *"Claim decisions in under ten days with the evidence attached."* | *"Migrate off email"* | Partner meeting + portal bulletin | EN |
| **`P06` Managers** | *"Your branch's position before anyone else sees it."* | *"Spreadsheets are being withdrawn"* | Manager briefing | EN |
| **`P12` Partners** | *"See your attributed revenue and your commission as it accrues."* | *"Improve attribution accuracy"* | Portal + partnerships | EN |

### 4.5 Internal adoption is not a campaign

**`UP-07`: internal adoption is driven by capability, support and management, not by marketing.**

`P02` technician adoption is the clearest case. It is a Critical risk (`RSK-008`) whose stated
mitigations are Bengali-first design, extreme simplicity, a field pilot with respected senior
technicians, Company-provided devices, incentive visibility, and the champion network — **none of
which is a campaign.** The corresponding entry in this file is therefore short by design:

| Internal audience | Adoption lever | Owned by |
|---|---|---|
| `P02` technicians | Device, training, champion, earnings visibility, field pilot | Operations, L&D, `CM-008` |
| `P03` branch and back office | Training, floor support, workaround withdrawal | Ops, `CM-007` |
| `P06` managers | Withdraw the source data for manual packs (`RSK-012` mitigation); require decisions to cite the dashboard | CEO, Ops |
| `P11` auditors | Paper audit forms withdrawn | Quality Manager |

> **`UP-08` — withdrawing the alternative is the strongest internal adoption lever available, and
> it is only usable once the replacement is proven.** `G2-09` withdraws paper service forms in
> Dhaka as a gate criterion. Withdrawal before capability is coercion, and it produces shadow
> spreadsheets rather than adoption.

### 4.6 Consent and channel

| # | Rule |
|---|---|
| **`UP-09`** | **Every external campaign message requires a lawful basis and a valid consent state** (`LG-008`, `MD-021`). A campaign is marketing; a transition notice is not (`MG-03`) |
| **`UP-10`** | Consent state is checked **at send**, not at list build |
| **`UP-11`** | Every campaign message carries a working opt-out in **both languages** |
| **`UP-12`** | Opt-out is **immediate and honoured across channels**, not per channel |
| **`UP-13`** | Frequency cap: no customer receives more than **two campaign messages in seven days**, and campaign and transition messages share the cap (`MG-16`) |
| **`UP-14`** | Suppression per `CM-013` §4.5 applies to campaigns without exception |
| **`UP-15`** | No campaign runs during a hypercare period at the affected sites (`CM-007`) |

### 4.7 The intervention ladder

`00-04` §5.5 requires *"intervention where lagging"*. What intervention means, in order:

| Step | Trigger | Action | Owner |
|:--:|---|---|---|
| 1 | A role or site below target for 2 weeks | **Diagnose** per §4.2 | Change Lead |
| 2 | Awareness gap confirmed | Targeted campaign to that audience only | Marketing |
| 3 | Capability gap confirmed | Refresher training; job aid (`TR-024`, `TR-022`) | L&D |
| 4 | Funnel or product gap confirmed | **Product finding to the squad**, with the step and the drop rate | Portal squad |
| 5 | Local management gap confirmed | Branch manager conversation | Operations Director |
| 6 | Below target at the gate | **`06-01` §9 contingency** — pause rollout, diagnose, remediate, re-pilot | Steering Committee |

> **`UP-16` — step 6 is a real option and is stated so that steps 1–5 are taken seriously.**
> `06-01` §9 already provides it; a programme that never uses it has decided adoption is
> negotiable.

### 4.8 Stop conditions

**`UP-17`: a campaign stops when its target is met, when its diagnosis is disproved, or when it
is doing harm.**

| Stop condition | Signal |
|---|---|
| Target met and held for four weeks | The measure |
| **Diagnosis disproved** | Awareness rises, adoption does not — the problem was question 3, 4 or 5 |
| Opt-out rate rising | The audience is being over-contacted |
| Complaint volume rising | The campaign is reaching people it should have suppressed |
| **Hypercare open at the target sites** | `UP-15` |
| Consent basis in question | Immediate stop pending Legal (`O-03`) |

### 4.9 Audience · channel · timing · message · call-to-action

| Audience | Channel | Timing | Message | Call to action |
|---|---|---|---|---|
| `P01` customers | In-app, portal, SMS to consenting, counter card | **Go + 2 weeks**, after transition | *"Book in three steps; see your technician"* | **Book your next service online** |
| `P02` technicians | Champion, supervisor, toolbox talk | From training | Earnings and offline capability | Use it for every job today |
| `P04` corporate | **Account manager 1:1** | Per account, from W4 | Bulk requests and SLA visibility | Book the setup session |
| `P05` vendors | Procurement officer + portal | From W3 | Payment and PO visibility | Acknowledge your next PO in the portal |
| `P07` sellers | In-app, cohort onboarding | From W7 | Payout speed and job match | Complete your profile; accept a job |
| `P08` brands | Partner meeting + bulletin | From W4 | Decision time and evidence | Submit your next claim in the portal |
| `P06` managers | Manager briefing | From W4 | Your branch's position, first | Use the dashboard in your weekly review |
| `S02` Steering | `CM-004` Section 5 | **Monthly** | **Worst-performing audience, with diagnosis** | Authorise the intervention |

### 4.10 Governing rules

| # | Rule | Class |
|---|---|:--:|
| `UP-01` | Every target is quoted from `04-00` or `06-02`, never invented | **H** |
| `UP-02` | A target with no captured baseline is not campaigned against | **H** |
| `UP-03` | A missed target is diagnosed through the six questions before a campaign is commissioned | **H** |
| `UP-04` | Only the awareness case is answered by a campaign | **H** |
| `UP-05` | "Active" is defined once, published, and changed only by a recorded decision | **H** |
| `UP-06` | Each audience is campaigned on a benefit to them | **H** |
| `UP-07` | Internal adoption is driven by capability, support and management, not marketing | **H** |
| `UP-08` | The alternative is withdrawn only after the replacement is proven | **H** |
| `UP-09` | Every external campaign message requires a lawful basis and a valid consent state | **H** |
| `UP-10` | Consent state is checked at send, not at list build | **H** |
| `UP-11` | Every campaign message carries a working opt-out in both languages | **H** |
| `UP-12` | Opt-out is immediate and cross-channel | **H** |
| `UP-13` | Two campaign messages per seven days, shared with the transition cap | **H** |
| `UP-14` | `CM-013` §4.5 suppression applies without exception | **H** |
| `UP-15` | No campaign runs during hypercare at the affected sites | **H** |
| `UP-16` | Persistent under-adoption at a gate invokes the `06-01` §9 contingency | **H** |
| `UP-17` | A campaign stops on target, on disproof, or on harm | **H** |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `04-00` §P01…§P12 | Every target and baseline in §4.1 |
| `06-02` §4 | The gate criteria that are adoption measures |
| `00-04` §5.5 | The monthly adoption report and the intervention requirement |
| `00-04` §1.2 `RSK-010`, `RSK-011`, `RSK-012` | The three adoption risks external and management campaigns address |
| [`CM-013_Customer_Migration_and_Transition_Pack.md`](CM-013_Customer_Migration_and_Transition_Pack.md) §4.5 | Suppression rules and the shared frequency cap |
| [`CM-014_Corporate_Client_Transition_Pack.md`](CM-014_Corporate_Client_Transition_Pack.md) · [`CM-015_Vendor_and_Seller_Transition_Pack.md`](CM-015_Vendor_and_Seller_Transition_Pack.md) | The transitions campaigns follow |
| [`CM-007_Hypercare_Communication_Pack.md`](CM-007_Hypercare_Communication_Pack.md) | `UP-15` quiet period |
| `LG-008` · `MD-021` | Lawful basis and consent state |
| `HC-016` · `UI-006` | In-product help and empty states — often the correct answer to question 3 |
| [`RP-001`](../14_Reporting_Analytics_and_KPI/RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md) · [`RP-015`](../14_Reporting_Analytics_and_KPI/RP-015_Benefits_Realisation_and_KPI_Baseline_Register.md) | The metric definitions `UP-05` requires, and the baseline register `UP-02` blocks against |
| `PS-10` | Analytics instrumentation on every critical funnel |

| Depended on by |
|---|
| `CM-004` Section 5 · `CM-007` exit adoption position · `CM-012` post-cutover site adoption · every gate criterion that is an adoption measure · `RSK-008`, `RSK-010`, `RSK-011`, `RSK-012` mitigation evidence |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Monthly during rollout**; targets reviewed at each wave gate |
| Trigger for out-of-cycle review | A target met early · a diagnosis disproved · a consent-basis change · a portal funnel change |
| Owner | Marketing with the Change Lead; external targets co-owned with the CCO |
| Change log | `RF-006`; a change to a target or to an "active" definition is a recorded decision, never an adjustment |
| Enforcement | `UP-01`…`UP-17`; the §4.2 diagnostic is completed and recorded before any campaign is commissioned |
| Improvement loop | **Every campaign records which of the six diagnostic questions it was answering.** Over nine waves this shows whether the programme's adoption problems are awareness problems — and the expectation, from `RSK-008` and `RSK-011`, is that most are not |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **Ten of the eighteen targets in §4.1 have no baseline, and the wider position is worse.** [`RP-015`](../14_Reporting_Analytics_and_KPI/RP-015_Benefits_Realisation_and_KPI_Baseline_Register.md) enumerates `06-02` §2 and finds **44 of 95 KPIs with no usable baseline — 46% of a BDT 876 lac benefit case**. `UP-02` blocks campaigning without one; `06-02` §6 blocks the benefit claim. Baseline capture must happen **before** each wave and appears in no plan | CCO with the PMO and the fourteen named benefit owners | **W2 minus 1 month, and before each subsequent wave** |
| **`O-02`** | **`UP-05` and `RP-001` must be reconciled, and neither cites the other.** [`RP-001`](../14_Reporting_Analytics_and_KPI/RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md) §`KPI-016` already makes this file's point independently — that a technician who opens the app and works from a paper notebook counts as active if the numerator is *"logged in"*. **`UP-05` requires "active" defined once and published; `RP-001` is where it must be published.** Until the two are joined, this file measures adoption against a definition the KPI dictionary has not ratified | Programme Content Lead with the BI Lead | **W2** |
| **`O-03`** | **The consent basis for external campaigns is unconfirmed.** `UP-09` requires a lawful basis and valid consent state; `DEP-34` records that PDPA transparency notice text does not exist, and `MD-021`'s consent state has no confirmed campaign semantics. `CM-013` `O-01` records the same exposure for transition messages, where the risk is lower because those are service communications | Legal with Marketing | **W2 minus 3 months** |
| **`O-04`** | **The Bengali counterpart does not exist**, and `P01`, `P02` and `P07` campaign content is Bengali-first for audiences of 250,000+, 200–400 and 500–2,000 respectively | Localisation Lead | **W2 minus 6 weeks** |
| **`O-05`** | **`UP-12` cross-channel opt-out has no mechanism.** Immediate, cross-channel opt-out honoured across SMS, WhatsApp, email, push and in-app requires a single preference store. `M27` is W4 and this file is W2 | CTO with Marketing | **W2 minus 2 months** |
| **`O-06`** | **The funnel instrumentation that answers diagnostic question 3 is unconfirmed.** `PS-10` requires analytics instrumentation on every critical funnel feeding `M25`; `M25` core lands at W4 and `P01` launches at W2. For two waves, question 3 cannot be answered with data, which means `UP-03` will be satisfied by opinion | CTO with the portal squads | **W2** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; §7 Open Items added per category convention
- [x] Category-standard audience · channel · timing · message · call-to-action table present (`CG-009` §3)
- [x] **Eighteen adoption targets registered, each quoted from `04-00` or `06-02` with its gate criterion where one exists**
- [x] Baseline requirement made blocking, with the ten missing baselines counted
- [x] **Six-question diagnostic placed before any campaign**, with only the awareness case answered by marketing
- [x] Measurement grain, cadence, denominator rule and a published "active" definition
- [x] Campaign reasons stated per audience as benefits to that audience, with the failing alternative shown
- [x] **Internal adoption explicitly excluded from campaigning**, with the withdrawal lever conditioned on proven capability
- [x] Consent, opt-out, frequency-cap and suppression rules aligned to `CM-013`
- [x] Six-step intervention ladder ending in the `06-01` §9 contingency
- [x] Stop conditions defined, including diagnosis disproof and harm
- [x] Seventeen governing rules with enforcement classes
- [x] All internal links resolve
- [ ] **`O-01` ten targets have no baseline**
- [ ] **`O-02` `UP-05` and `RP-001` `KPI-016` not reconciled; “active” unratified**
- [ ] **`O-03` consent basis for external campaigns unconfirmed**
- [ ] **`O-04` Bengali counterpart not written**
- [ ] **`O-06` funnel instrumentation unavailable for the first two waves**
- [ ] Named approver recorded — **pending Content Design Lead with Legal and the CCO**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
