---
id: HC-004
title: Help Set — P02 Technician App
project: 1000FiX ERP System v2.0
content_type: Help article
template: TPL_Help_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design
author: Content Design with Technical Services
reviewers: [Technical Director, Operations Director, HSE Lead, Knowledge Manager, Localisation Lead, Accessibility reviewer]
approver: Content Design Lead with Technical Director
content_class: D
purpose: >
  The in-app help set for 200–400 field technicians covering job execution, parts, evidence,
  offline working, sync, payments, safety and escalation. Delivered offline and in Bengali, because
  a technician cannot browse a website mid-job — and because P02's daily active usage target above
  95% collapses the moment the app cannot answer a question at the point of work.
traces_to: [P02, M01, M02, M22, M31, M61, MD-024, MD-025, MD-026, HC-001, HC-002, HC-016, UI-012, UI-009, KB-013, KB-016, TR-009, TR-022, SP-008, SP-016, SP-030]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: HC-004_Help_Set_P02_Technician_App_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P02 non-negotiables include complete Bengali UI including error messages, full offline operation for 24 hours, offline access to repair manuals and past repair notes; daily active usage target above 95%
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §6 T-01 offline set scoping and T-03 staleness visible offline; §5.2 FR-KMS-017/018
    verified: 2026-08-18
    class: P1
  - source: project_content/07_Knowledge_Base_and_Technical_Library/KB-016_Technician_Field_Reference_Card_Set.md §3.1 and §6.2 — the offline card set, its layers and the RC-01 derivation rule; the CP-01 boundary this help set must respect
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Help Set — P02 Technician App

| Item | Value |
|---|---|
| Portal | `P02` Technician Mobile |
| Audience | **Field technician** — audience 2 · 200–400, mixed literacy, high turnover |
| Article type | Help set specification — Task and Troubleshooting predominate |
| Reading level target | `CG-011`; **visual-first for mixed literacy** |
| Languages | **Bengali authored** (`HS-29`) |
| Related UI copy | `UI-012` `P02` copy pack · `UI-009` offline and sync copy |

> **Template conformance.** As `HC-003`: `TPL_Help_Article.md` applied at set level, all sections
> retained in order with set-level interpretation. Additions justified where they appear.

---

## Before you start

| Prerequisite | Why |
|---|---|
| [`../HC-001_Help_Centre_Information_Architecture.md`](../HC-001_Help_Centre_Information_Architecture.md) · [`../HC-002_Help_Article_Template_and_Style_Rules.md`](../HC-002_Help_Article_Template_and_Style_Rules.md) | Architecture and article shape |
| `UI-012`, `UI-009` | Labels and offline-state copy quoted in steps |
| [`../../07_Knowledge_Base_and_Technical_Library/KB-016_Technician_Field_Reference_Card_Set.md`](../../07_Knowledge_Base_and_Technical_Library/KB-016_Technician_Field_Reference_Card_Set.md) | **The boundary — see below** |
| [`../../08_Training_and_Enablement/08B_Course_Packs/TR-009_Course_Pack_Field_Technician.md`](../../08_Training_and_Enablement/08B_Course_Packs/TR-009_Course_Pack_Field_Technician.md) | This set assumes the technician was trained; it is a reminder layer |

**`PS-05`: the three-way boundary that this set must not blur.**

| Question | Owner |
|---|---|
| *"Is this safe? What does this fault mean technically?"* | **`KB-016`** offline cards |
| *"How do I record this in the app?"* | **`HC-004`** — this set |
| *"How do I do this task in the system, as a trained user?"* | **`TR-022`** job aids |

`AUDIT-008` KB-09 resolved the `TR-022` / `KB-016` boundary; this set is the third party to it.
**`PS-06`: where the three overlap, the artefact is authored once and referenced** (`CP-01`).

---

## Steps — *the technician's day and its article inventory*

### Block A — The job *(9 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 1 | **Accept and start a job** | Task | **P0** |
| 2 | Find the job's history and past repairs | Task | P1 |
| 3 | Record what you found | Task | **P0** |
| 4 | **Code the fault** — and when to use "cannot determine" | Task | **P0** |
| 5 | Build and send an estimate | Task | **P0** |
| 6 | Record what you did and close the job | Task | **P0** |
| 7 | Put a job on hold | Task | P1 |
| 8 | Hand a job to someone else | Task | P1 |
| 9 | The job isn't in my list | Troubleshooting | P1 |

### Block B — Offline and sync *(6 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 10 | **Working with no signal — what still works** | Concept | **P0** |
| 11 | **Check what has synced before you leave** | Task | **P0** |
| 12 | Sync failed | Troubleshooting | **P0** |
| 13 | Someone else changed the job while I was offline | Troubleshooting | P1 |
| 14 | My offline pack is out of date | Troubleshooting | P1 |
| 15 | Storage is full | Troubleshooting | P2 |

### Block C — Parts and evidence *(7 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 16 | Request a part | Task | **P0** |
| 17 | Record parts used and returned | Task | **P0** |
| 18 | Van stock — check and reconcile | Task | P1 |
| 19 | The system won't let me issue this part | **Troubleshooting** | **P0** — `BRU-SRM-11` |
| 20 | **Take the photographs a claim needs** | Task | **P0** |
| 21 | Capture a signature | Task | P1 |
| 22 | Photograph won't upload | Troubleshooting | P1 |

### Block D — Money and customer *(5 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 23 | Take a payment in the field | Task | **P0** |
| 24 | Payment failed at the customer's door | Troubleshooting | **P0** |
| 25 | Issue a receipt | Task | P1 |
| 26 | The customer declined the estimate | Task | P1 |
| 27 | The customer isn't there | Troubleshooting | P1 |

### Block E — Safety and escalation *(6 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 28 | **Report a safety incident from the app** | Task | **P0** |
| 29 | **This job is above my level** — escalate | Task | **P0** |
| 30 | Ask for help without leaving the job | Task | P1 |
| 31 | Report a device that is unsafe | Task | **P0** |
| 32 | My equipment has failed a check | Task | P1 |
| 33 | I can't work safely here | **Task — the right to refuse** | **P0** |

### Block F — Learning and knowledge *(4 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 34 | Find a repair procedure offline | Task | P1 |
| 35 | **Capture what you learned in three minutes** | Task | P1 — `FR-KMS-024` |
| 36 | Do your assigned learning | Task | P2 — `FR-LMS-025` |
| 37 | Rate whether an article helped | Task | P2 |

**Set total: 37 articles · 17 at P0 · 14 at P1 · 6 at P2 · 0 at P3.**

---

## What happens next

| Outcome | Measure | Target |
|---|---|---|
| Technicians use the app rather than reverting to paper | **`P02` daily active usage** | **> 95%** |
| Questions answered in the app, not by phoning a supervisor | Supervisor interruption volume | Falling |
| Offline work is captured and synced | Sync failure rate; unsynced-at-shift-end | Approaching zero |
| Evidence is complete on first submission | Claim rejections for missing evidence | Falling (`BRU-WTY-01`) |

**`PS-07`: articles 10, 11 and 12 carry this set.** Offline confidence is the difference between a
technician who trusts the app and one who keeps a paper notebook, and the paper notebook is
invisible to every measure the programme has.

---

## If it does not work

| Symptom | Cause | What to do |
|---|---|---|
| Daily active usage below 95% | The app failed them offline, or the Bengali does not read naturally | **Investigate the product and the content, not the workforce** (`TR-009` §10) |
| Technicians photograph help and share it in chat | Help is not reaching the device, or the offline pack is stale | Pack telemetry; `KB-016` `RC-03` |
| Help opened but supervisor still called | The article does not answer the real question | Re-derive from actual escalation topics |
| Safety articles unread | Buried; or duplicated against `KB-016` and the technician does not know which is current | **`PS-06`** — author once, reference |
| Article contradicts a `KB-016` card | Boundary breached | Withdraw; Knowledge Manager and Content Design jointly |

---

## Related

[`../../07_Knowledge_Base_and_Technical_Library/KB-016_Technician_Field_Reference_Card_Set.md`](../../07_Knowledge_Base_and_Technical_Library/KB-016_Technician_Field_Reference_Card_Set.md) · [`../../07_Knowledge_Base_and_Technical_Library/KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](../../07_Knowledge_Base_and_Technical_Library/KB-013_ESD_Chemical_and_Battery_Safety_Data.md) ·
[`../../08_Training_and_Enablement/08B_Course_Packs/TR-009_Course_Pack_Field_Technician.md`](../../08_Training_and_Enablement/08B_Course_Packs/TR-009_Course_Pack_Field_Technician.md) · [`../../08_Training_and_Enablement/08B_Course_Packs/TR-022_Job_Aid_and_Quick_Reference_Library.md`](../../08_Training_and_Enablement/08B_Course_Packs/TR-022_Job_Aid_and_Quick_Reference_Library.md) ·
[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-008_SOP_On_Site_Field_Service_Visit.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-008_SOP_On_Site_Field_Service_Visit.md) · [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md) ·
`UI-012`, `UI-009` · [`../HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md`](../HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md) · [`HC-011_Help_Set_P09_Logistics_and_Rider_App.md`](HC-011_Help_Set_P09_Logistics_and_Rider_App.md) — the same offline-first pattern.

---

## Feedback

In-app helpfulness per `CG-014`, capturable **offline** and replayed on sync (`M61` T-08 pattern).
Reported weekly with usage and sync telemetry.

---

## Coverage and Authoring Plan *(addition — justified as in `HC-003`)*

| Item | Position |
|---|---|
| Articles required | **37** · written **0** |
| Effort | 37 × 2–3 h = **75–110 hours**, plus Bengali authoring |
| Sequencing | Articles 10, 11, 12 (`PS-07`) then the 17 P0 before W2 release |
| Delivery | **In-app and offline** — a help set behind a network call is not a help set for this audience |
| Bengali | All 37, authored in Bengali |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **Offline help delivery inside `P02` must exist at W2.** `M61` provides the offline mechanism at **W6**; without an interim path this set is a website 200–400 technicians cannot reach mid-job | CTO with Content Design | **W2 — blocking the delivery model** |
| **O-02** | **The `PS-06` author-once rule needs a joint owner** across `HC-004`, `KB-016` and `TR-022`. `TR-022` `O-02` records the same unowned boundary | Programme Content Lead | **W2** |
| **O-03** | Bengali authoring capability (`TR-001` `O-05`, `KB-002` `O-05`) | Localisation Lead | **W2** |
| **O-04** | Articles 4, 34 and 35 depend on `MD-024`/`MD-025` codes and `KB` articles that are unpopulated or unwritten (`AUDIT-008`) | Technical Director with MDM | W2 |
| **O-05** | The offline help page-weight budget is unspecified — the same gap `HC-002` `O-06` records, and it binds harder here | CTO | W2 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Help_Article.md` at set level; additions justified
- [x] **Three-way boundary with `KB-016` and `TR-022` stated and the author-once rule set (`PS-05`, `PS-06`)**
- [x] Organised by the technician's day; 37 articles enumerated with type and priority
- [x] The three articles carrying the set identified (`PS-07`)
- [x] Offline-first delivery treated as a design condition, not a feature
- [x] Usage failure diagnosed to product and content rather than to the workforce
- [x] The right to refuse unsafe work included as an article (33)
- [x] All internal links resolve
- [x] `FR-KMS-*`, `FR-LMS-025` cited to their modules; `BRU-SRM-11`, `BRU-WTY-01` to `05-05`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 37 articles authored — outstanding**
- [ ] **`O-01` offline delivery at W2 — outstanding; blocking**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and Technical Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
