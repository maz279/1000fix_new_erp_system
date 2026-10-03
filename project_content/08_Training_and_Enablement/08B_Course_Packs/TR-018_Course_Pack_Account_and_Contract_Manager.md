---
id: TR-018
title: Course Pack — Account and Contract Manager
project: 1000FiX ERP System v2.0
content_type: Training course pack
template: TPL_Training_Course_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Learning & Development
author: Learning & Development with Account Management and Commercial
reviewers: [Chief Commercial Officer, Finance Manager, Legal Counsel, Operations Director, Quality Manager, Localisation Lead]
approver: Chief Commercial Officer with Finance Manager
content_class: D
purpose: >
  Trains account and contract managers who own contract value, renewal and the corporate
  relationships that are the highest-value customer segment. Contract revenue is recurring and
  compounding, so leakage at any lifecycle stage is permanent — an entitlement not tracked, a
  renewal missed or an SLA credit not understood is margin that never returns.
traces_to: [M07, M08, M11, M35, M36, M39, M22, P04, P06, MD-015, MD-029, MD-032, MD-028, TR-001, TR-002, TR-004, TR-006, TR-022, UI-032, SP-015, SP-004, LG-015]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: TR-018_Course_Pack_Account_and_Contract_Manager_BN.md
sources:
  - source: project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-015_SOP_Contract_and_AMC_Lifecycle.md — qualification, quotation, approval, activation, entitlement management, amendment, renewal, termination
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-CTR family; BRU-SRM-03 contract-type orders blocked unless the device is on an active contract's covered-asset list; BR-STD-06 override discipline
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P04 corporate portal with delegated approval chains and consolidated billing; invoice dispute target below 3%
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# Course Pack — Account and Contract Manager

| Item | Value |
|---|---|
| Audience role(s) | `R22` Account Manager (Corporate) · `R21` Sales Manager · **`R23` Marketing Manager (delta, `TR-002` §7.4)** |
| Headcount | `R22` 8–20 · `R21` 3–6 · `R23` 2–4 |
| Duration | **Core 8 hours** over two days · **marketing delta 3 h** |
| Delivery mode | Classroom with sandbox |
| Language | English primary with Bengali parallel (`DS-18`) |
| Prerequisites | Layer 1 universal core |
| Certification outcome | Functional competence record (`TR-006` cell 8) |
| Wave | W2 |

> **This pack carries `R23` Marketing Manager** as an interim route under `TR-002` §7.4, because no
> pack exists for `M35`. `CU-16` requires the compromise to be declared; §3.2 declares it.

---

## 1. Learning Objectives

| # | On completion the learner can… | Assessed by |
|---|---|---|
| 1 | Qualify, quote, approve and activate a contract to `SP-015` | Sandbox + practical |
| 2 | **Manage the covered-asset list**, and explain why a device not on it cannot be serviced under contract | Items — `BRU-SRM-03` |
| 3 | Track entitlement consumption and recognise leakage before renewal | Sandbox |
| 4 | Run a renewal on time, with the value conversation prepared | Role play |
| 5 | Amend a contract without breaking billing or entitlement | Sandbox |
| 6 | **Explain SLA and service credits accurately** — what is promised and what it costs when missed | **Critical items** — `MD-028`, `LG-015` |
| 7 | Set up a corporate hierarchy with delegated approval and consolidated billing | Sandbox — `MD-015`, `P04` |
| 8 | Apply discount authority correctly and log every exception | Items — `SP-004`, `BR-STD-06` |
| 9 | Handle an invoice dispute to resolution | Role play — `P04` target < 3% |
| 10 | *(Marketing delta)* Run a campaign within consent, data-protection and brand constraints | Items — `LG-008` |

---

## 2. Curriculum Position

| Precedes | Follows | Refreshed every |
|---|---|---|
| Contract authority · `P04` account ownership | Layer 1 core | On release (`TR-024`); 24 months. **Pricing and SLA content on any rate-card or `LG-015` change** |

---

## 3. Module Outline

### 3.1 Core — 8 hours

| # | Module | Duration | Method |
|---:|---|---|---|
| 1 | Contract revenue: recurring, compounding, and permanently lost when leaked | 30 min | Facilitated |
| 2 | The contract lifecycle end to end | 75 min | Walkthrough — `SP-015`, `UI-032` |
| 3 | **Covered assets and the hard block** | 60 min | Items + sandbox — `BRU-SRM-03` |
| 4 | Entitlement tracking and leakage detection | 75 min | Sandbox |
| 5 | **SLA, service credits and what we actually promised** | 75 min | Items — `MD-028`, `LG-015` |
| 6 | Renewal — timing, value conversation, escalation | 60 min | Role play |
| 7 | Amendment without breaking billing | 45 min | Sandbox |
| 8 | **Corporate hierarchy, delegated approval, consolidated billing** | 75 min | Sandbox — `MD-015`, `P04` |
| 9 | Discount authority and exception logging | 45 min | Items — `SP-004` |
| 10 | Invoice disputes — cause and cure | 45 min | Role play |
| 11 | Reading account health in `P06` | 30 min | Walkthrough |
| | **Total** | **~8 hours** | |

### 3.2 Marketing delta — 3 hours (`R23`) — *declared interim route*

Campaign setup and targeting · **consent and data-protection constraints** (`LG-008`, `LG-011`) ·
segment definitions (`MD-014`) · voucher and promotion rules (`MD-030`) · brand and naming standards
(`VB-010`) · what may be said about a product or a partner (`AU-20`).

**`PK-09`: this delta is an interim control.** `R23` performs a distinct role with consent and
data-protection obligations that a contract pack is not designed to carry. Gap: `TR-002` `O-03`.

---

## 4. Facilitator Guide

| Module | Talking points | Common misconceptions |
|---|---|---|
| 1 | A contract lost at renewal is not one sale lost; it is every future year lost at once | *"We'll win it back next year."* |
| 3 | `BRU-SRM-03` blocks contract-type orders for devices not on the covered-asset list. **The block is protecting the margin the contract was priced on** | *"They're a contract customer, just book it."* |
| 5 | Service credits are a financial liability with a contractual trigger. **Explaining SLA loosely to win a deal creates a cost the delivery teams must then absorb** | *"We'll sort the details later."* |
| 6 | A renewal conversation prepared two weeks out is a negotiation. One prepared two days out is a concession | *"They always renew."* |
| 8 | `P04`'s delegated approval exists because corporate customers have their own controls. Setting it up wrongly creates disputes on every invoice | *"One admin user is simpler."* |
| 10 | The invoice dispute target is under 3%. **Most disputes originate in how the contract was set up, not in how the invoice was produced** | *"That's finance's problem."* |

---

## 5. Participant Workbook Contents

Contract lifecycle map (`SP-015`) · covered-asset rules · entitlement tracking guide · **SLA and
service-credit table** (`MD-028`, `LG-015`) · renewal timeline and preparation checklist · amendment
impact guide · **corporate hierarchy and delegated approval setup** · discount authority (`SP-004`)
· dispute causes and cures · *(delta)* **consent and campaign constraints** · **my access scope and
discount limits**.

---

## 6. Exercises

| # | Exercise | Sandbox | Test data (`TS-002`) | Success criterion |
|---|---|---|---|---|
| 1 | Qualify and quote a contract | Sandbox | Corporate opportunity | Correct rate card and terms |
| 2 | **Covered-asset block** | Sandbox | Device not on the list | Block respected; correct remedy offered |
| 3 | Entitlement review with leakage | Sandbox | Contract with over-consumption | Leakage found and actioned |
| 4 | **SLA explanation role play** | Role play | Customer asks what happens on a miss | Accurate; credits explained correctly |
| 5 | Renewal preparation and conversation | Role play | Contract 60 days from expiry | Prepared, value-based, escalation ready |
| 6 | Amendment with billing impact | Sandbox | Mid-term change | Billing and entitlement both correct |
| 7 | **Corporate hierarchy setup** | Sandbox | Group with three sites and two approvers | Approval chain and billing correct |
| 8 | Discount above authority | Scenario | Request beyond limit | Escalates; logs the exception |
| 9 | Invoice dispute | Role play | Disputed consolidated invoice | Resolved or correctly escalated; root cause identified |
| 10 | *(Delta)* Campaign within consent | Scenario | Campaign targeting an unconsented segment | Recognises the constraint; adjusts |

---

## 7. Assessment

| Item | Weight | Pass mark | Attempts | Re-certification |
|---|---:|---:|---:|---|
| `TR-006` cell 8 form, 30 items | 30% | 80%, **100% on SLA, credit and covered-asset items** | 3 | 24 months |
| Sandbox (1, 2, 3, 6, 7) | 30% | All passed | 3 | 24 months |
| **SLA and renewal role plays (4, 5)** | 25% | Both passed | 3 | 24 months |
| Discount and dispute (8, 9) | 15% | Both passed | 3 | 24 months |
| *(Delta)* exercise 10 | Gate for `R23` | Passed | 3 | Annual |
| **OJT sign-off — 3 contracts observed end to end** | Gate | Chief Commercial Officer delegate | — | — |

---

## 8. Job Aids Produced

Contract lifecycle map · covered-asset rule card · **SLA and service-credit table** · renewal
preparation checklist · amendment impact guide · corporate hierarchy setup guide · discount
authority card · dispute cause-and-cure card · *(delta)* consent constraints card. All in `TR-022`.

---

## 9. Trainer Requirements

L&D with an experienced account manager co-delivering · **Legal for module 5 and the delta** ·
Finance for module 8 and 10 · sandbox with corporate hierarchies and contracts · cohort maximum 12.

---

## 10. Evaluation

| Level | Measure | Target |
|---|---|---|
| **Reaction** | Confidence explaining SLA and running a renewal | Diagnostic only (`LS-02`) |
| **Learning** | Assessment and role-play pass | > 85% first attempt |
| **Behaviour** | Renewal timeliness · entitlement leakage detected · covered-asset block overrides attempted · discount exceptions logged | Leakage falling; overrides zero |
| **Result** | Contract renewal rate · contract margin · **`P04` invoice dispute rate below 3%** · service-credit exposure | Per `04-00` `P04`, `RP-001` |

**Required Drivers** (`LS-04`): reinforce — SLA table and renewal checklist · encourage — CCO
reviews the first three renewals · monitor — renewal timeliness and leakage · reward — competence
record; account performance in `P06`.

---

## 11. Related Documents

[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-015_SOP_Contract_and_AMC_Lifecycle.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-015_SOP_Contract_and_AMC_Lifecycle.md) ·
[`../../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md`](../../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md) ·
[`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-015_Corporate_Account_Hierarchy_Standard.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-015_Corporate_Account_Hierarchy_Standard.md) ·
[`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md) ·
`LG-015` AMC SLA master terms and service-credit rules · `UI-032` contract console copy ·
[`../08A_Framework/TR-006_Question_Bank_Functional_Roles.md`](../08A_Framework/TR-006_Question_Bank_Functional_Roles.md) cell 8.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`LG-015` SLA master terms and service-credit rules are unwritten** (Category 10 unstarted). Module 5 — the pack's highest-consequence content — has no governing source | Legal Counsel with Commercial | **W2 — blocking module 5** |
| **O-02** | `TS-002` sandbox with corporate hierarchies and contracts does not exist | Test Lead with Commercial | W2 |
| **O-03** | **The `R23` delta (§3.2) is an interim control** carrying consent and data-protection obligations. `LG-008` and `LG-011` are also unwritten | Training Lead with Legal | W2 |
| **O-04** | `MD-032` contract templates and `MD-029` rate cards are unpopulated; modules 1–3 teach against empty registers | Commercial with MDM | W2 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Training_Course_Pack.md` — all ten sections in order; §11 and Open Items added per category convention
- [x] Objectives observable (`DS-02`); Level 4 measures named (`LS-01`)
- [x] **`R23` interim route declared (`PK-09`, `CU-16`)**
- [x] SLA and service credits taught as financial liability with critical assessment items
- [x] Covered-asset block taught as margin protection rather than obstruction
- [x] Invoice disputes traced to contract setup rather than to billing
- [x] OJT sign-off gate present (`LS-03`); all four Required Drivers named (`LS-04`)
- [x] All internal links resolve
- [x] `BRU-SRM-03`, `BR-STD-06` cited to `05-05`; `P04` targets to `04-00`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` `LG-015` — outstanding; blocks the SLA module**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending CCO and Finance Manager**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
