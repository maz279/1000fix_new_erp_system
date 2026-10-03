---
id: HC-006
title: Help Set — P04 Corporate B2B Portal
project: 1000FiX ERP System v2.0
content_type: Help article
template: TPL_Help_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design
author: Content Design with Account Management
reviewers: [Chief Commercial Officer, Account Managers, Finance Manager, Legal Counsel, Localisation Lead, Accessibility reviewer]
approver: Content Design Lead with Chief Commercial Officer
content_class: D
purpose: >
  The self-service help set for 500–2,000 corporate portal users covering estate management, bulk
  requests, delegated approvals, SLA, consolidated billing, reporting and compliance downloads.
  Corporate administrators are unpaid users of the company's system: friction here is not a support
  cost, it is a contract-renewal risk, and every unanswered question arrives as an invoice dispute.
traces_to: [P04, M05, M07, M08, M20, M25, M61, MD-015, MD-028, HC-001, HC-002, HC-008, HC-016, UI-014, LG-003, LG-015, TR-018]
priority: P2
wave: W4
bilingual: yes
bn_counterpart: HC-006_Help_Set_P04_Corporate_B2B_Portal_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P04 serves 500–2,000 corporate users with delegated approval chains and consolidated billing; invoice dispute target below 3%
    verified: 2026-08-18
    class: P1
  - source: project_content/08_Training_and_Enablement/08B_Course_Packs/TR-018_Course_Pack_Account_and_Contract_Manager.md §4 — most invoice disputes originate in how the contract was set up, not in how the invoice was produced
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Help Set — P04 Corporate B2B Portal

| Item | Value |
|---|---|
| Portal | `P04` Corporate B2B |
| Audience | **Corporate customer administrator** — audience 4 · 500–2,000 |
| Article type | Help set specification — Task and Concept predominate |
| Reading level target | `CG-011`; business audience, no technical assumption |
| Languages | Bengali and English; **English primary for many corporate users** |
| Related UI copy | `UI-014` `P04` copy pack |

> **Template conformance.** As `HC-003`, applied at set level.

---

## Before you start

| Prerequisite | Why |
|---|---|
| [`../HC-001_Help_Centre_Information_Architecture.md`](../HC-001_Help_Centre_Information_Architecture.md) · [`../HC-002_Help_Article_Template_and_Style_Rules.md`](../HC-002_Help_Article_Template_and_Style_Rules.md) | Architecture and shape |
| `UI-014` | Labels quoted in steps |
| `LG-003` corporate portal terms · `LG-015` AMC SLA master terms | Linked, never restated (`IA-14`, `IA-15`) |
| [`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-015_Corporate_Account_Hierarchy_Standard.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-015_Corporate_Account_Hierarchy_Standard.md) | Hierarchy and approval structures the articles describe |

**`PS-10`: the reader is not our employee and has not been trained.** They administer their
company's account as a small part of another job. Every article assumes a first-time reader with no
patience and a real deadline.

---

## Steps — *the corporate administrator's journey*

### Block A — Set up and access *(7 articles)*

Getting started with your company account · **your company's structure, sites and departments** ·
add and remove users · **who can approve what** (delegated approval) · set spending limits ·
single sign-on · your role and what it permits. **2 at P0, 4 at P1, 1 at P2.**

### Block B — Requests and estate *(9 articles)*

Raise a service request · **raise many at once (bulk)** · request on behalf of a colleague · track
all your company's requests · **your device estate — what we hold** · add or retire a device ·
scheduled and preventive visits · **priority and what it costs** · cancel or amend. **3 at P0,
4 at P1, 2 at P2.**

### Block C — Approvals *(5 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 17 | **Approve a request or an estimate** | Task | **P0** |
| 18 | **Why this needs your approval** | Concept | **P0** |
| 19 | Approve on someone's behalf / delegation | Task | P1 |
| 20 | An approval is stuck | Troubleshooting | P1 |
| 21 | Change your approval chain | Task | P2 |

### Block D — Money and billing *(8 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 22 | **Understand your consolidated invoice** | Concept | **P0** |
| 23 | **Query a line on your invoice** | Task | **P0** |
| 24 | Cost centre and department allocation | Concept | P1 |
| 25 | Download invoices and statements | Task | P1 |
| 26 | Pay an invoice | Task | P1 |
| 27 | Your contract and what it includes | Concept | P1 |
| 28 | Your entitlement — what you have used | Concept | P1 |
| 29 | Renewal — what happens and when | Concept | P2 |

### Block E — SLA, reporting and compliance *(7 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 30 | **What SLA you have and how it is measured** | Concept | **P0** — links `LG-015` |
| 31 | **When we miss an SLA** | Concept | **P0** |
| 32 | Your reports and dashboards | Task | P1 |
| 33 | Schedule a report to your inbox | Task | P2 |
| 34 | **Download compliance and disposal certificates** | Task | P1 |
| 35 | Export your data | Task | P2 |
| 36 | Raise a complaint or escalate | Task | P1 |

**Set total: 36 articles · 8 at P0 · 18 at P1 · 10 at P2.**

---

## What happens next

| Outcome | Measure | Target |
|---|---|---|
| Corporate users self-serve rather than emailing their account manager | Account-manager query volume per account | Falling |
| Invoices are understood before they are disputed | **`P04` invoice dispute rate** | **Below 3%** |
| Approvals do not stall | Approval cycle time | Falling |
| SLA expectations match reality | SLA-related escalations | Falling |

**`PS-11`: articles 22, 23, 30 and 31 carry this set.** `TR-018` records that most invoice disputes
originate in contract setup rather than billing — but the *dispute itself* starts when an
administrator cannot understand a line on a consolidated invoice at 6 p.m. Those four articles are
the difference between a query and a dispute.

---

## If it does not work

| Symptom | Cause | What to do |
|---|---|---|
| Dispute rate above 3% | Invoice structure not explained, or contract setup wrong upstream | Check article 22 usage before blaming billing |
| Account managers still fielding routine questions | Help not discoverable inside `P04` | `HC-016` contextual entry |
| Approvals stalling | Delegation not understood, or the chain was set up wrongly | Articles 19, 21; escalate hierarchy setup to `TR-018` |
| SLA arguments | Article 30 restated the SLA instead of linking it | `IA-14`, `IA-15` breached — withdraw and correct |

---

## Related

`UI-014` · [`HC-008_Help_Set_P06_Analytics_and_Executive_Dashboard.md`](HC-008_Help_Set_P06_Analytics_and_Executive_Dashboard.md) — corporate users consume analytics in `P04` ·
[`../../08_Training_and_Enablement/08B_Course_Packs/TR-018_Course_Pack_Account_and_Contract_Manager.md`](../../08_Training_and_Enablement/08B_Course_Packs/TR-018_Course_Pack_Account_and_Contract_Manager.md) — the internal counterpart ·
[`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md) · `LG-003`, `LG-015` ·
Category 18 `EO` — corporate onboarding content (**boundary, `O-03`**).

---

## Feedback

Helpfulness per `CG-014`, plus **dispute-origin analysis**: every invoice dispute is checked for
whether an article existed and was read.

---

## Coverage and Authoring Plan *(addition)*

| Item | Position |
|---|---|
| Articles required | **36** · written **0** |
| Effort | 36 × 2–3 h = **70–110 hours** |
| Sequencing | The 4 dispute-preventing articles (`PS-11`), then 8 P0 before W4 |
| Bengali | Both languages; **English may be primary** for this audience (`HS-30`) |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`LG-003` and `LG-015` are unwritten** (Category 10 unstarted). Articles 27, 30 and 31 link to legal artefacts that do not exist | Legal Counsel | **W4** |
| **O-02** | `MD-015` corporate hierarchy is unpopulated; Block A teaches structures with no live example | MDM with Account Management | W4 |
| **O-03** | **The boundary with Category 18 `EO` corporate onboarding is undefined** — `HC-001` `O-06` records it for all four external audiences | Programme Content Lead | W3 |
| **O-04** | Article 34 compliance certificates depend on `M18` and `DT-035`; availability at W4 unconfirmed | Sustainability with CTO | W4 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Help_Article.md` at set level; additions justified
- [x] Reader assumed untrained and time-poor (`PS-10`)
- [x] 36 articles enumerated with type and priority
- [x] The four dispute-preventing articles identified (`PS-11`)
- [x] SLA linked, never restated (`IA-14`, `IA-15`)
- [x] All internal links resolve
- [x] `P04` dispute target cited to `04-00`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` legal artefacts — outstanding**
- [ ] **`O-03` `EO` boundary — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and CCO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
