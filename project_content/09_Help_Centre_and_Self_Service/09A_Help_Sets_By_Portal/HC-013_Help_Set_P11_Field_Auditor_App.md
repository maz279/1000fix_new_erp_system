---
id: HC-013
title: Help Set — P11 Field Auditor App
project: 1000FiX ERP System v2.0
content_type: Help article
template: TPL_Help_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design
author: Content Design with Quality Management
reviewers: [Quality Manager, Operations Director, Localisation Lead, Accessibility reviewer, Programme Content Lead]
approver: Content Design Lead with Quality Manager
content_class: D
purpose: >
  The in-app help set for field auditors covering the audit programme, offline execution, findings,
  verification and reporting. Auditors work at branches with poor connectivity against
  clause-referenced checklists, and an auditor who cannot classify a finding consistently produces
  audit data that cannot be aggregated — which is the whole value of auditing.
traces_to: [P11, M23, M61, MD-026, MD-046, HC-001, HC-002, HC-016, UI-021, TR-016, SP-029, SP-032, LG-022]
priority: P3
wave: W5
bilingual: yes
bn_counterpart: HC-013_Help_Set_P11_Field_Auditor_App_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P11 field auditor app; 20–60 auditors; audit findings must be classified consistently
    verified: 2026-08-18
    class: P1
  - source: project_content/08_Training_and_Enablement/08B_Course_Packs/TR-016_Course_Pack_Quality_and_Field_Auditor.md §1.1 and §3.2 — the auditor population is not a registered role, and classification consistency is sustained by six-monthly calibration
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-QMS-01 a checklist cannot be marked complete with unanswered mandatory items; BRU-QMS-02 every non-conformance requires a root cause and a CAPA before closure
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Help Set — P11 Field Auditor App

| Item | Value |
|---|---|
| Portal | `P11` Field Auditor |
| Audience | **Field auditor** — audience 10 · 20–60 · **not a registered role** (`TR-016` §1.1, `TR-002` `O-05`) |
| Article type | Help set specification — Task and Concept |
| Reading level target | `CG-011`; trained audience using ISO vocabulary |
| Languages | Bengali primary for branch auditing; English parallel |
| Related UI copy | `UI-021` `P11` auditor app copy pack |

> **Template conformance.** As `HC-003`, applied at set level. **Offline-first**, as `HC-004` and
> `HC-011`.

---

## Before you start

| Prerequisite | Why |
|---|---|
| [`../HC-001_Help_Centre_Information_Architecture.md`](../HC-001_Help_Centre_Information_Architecture.md) · [`../HC-002_Help_Article_Template_and_Style_Rules.md`](../HC-002_Help_Article_Template_and_Style_Rules.md) | Architecture and shape |
| `UI-021` | Labels quoted in steps |
| [`../../08_Training_and_Enablement/08B_Course_Packs/TR-016_Course_Pack_Quality_and_Field_Auditor.md`](../../08_Training_and_Enablement/08B_Course_Packs/TR-016_Course_Pack_Quality_and_Field_Auditor.md) | **The boundary — see below** |
| [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) | The process the app executes |

**`PS-29`: classification consistency is `TR-016`'s job, not this set's.** `TR-016` §3.2 sustains it
through six-monthly calibration against a reference case set. **This set explains how to record a
classification in the app; it must not become a second, uncalibrated classification guide** —
that would put two definitions over one judgement (`CP-01`, `IA-12`).

---

## Steps — *the audit and its article inventory*

### Block A — Before the visit *(5 articles)*

Your audit plan · download an audit for offline use · **what to prepare** · the checklist and its
clause references · notify the site. **1 at P0, 3 at P1, 1 at P2.**

### Block B — On site, offline *(7 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 6 | **Work an audit with no signal** | Concept | **P0** |
| 7 | Complete a checklist | Task | **P0** |
| 8 | **A mandatory item you cannot answer** | Troubleshooting | **P0** — `BRU-QMS-01` |
| 9 | Capture evidence — photograph, note, document | Task | **P0** |
| 10 | Record a finding | Task | **P0** |
| 11 | **Classify a finding** *(recording only — see `PS-29`)* | Task | **P0** |
| 12 | **Check what has synced before you leave the site** | Task | **P0** |

### Block C — Findings and CAPA *(6 articles)*

Assign a CAPA · set an owner and a due date · **link a finding to a previous one** · verify
effectiveness · close or reopen · escalate a safety finding immediately. **2 at P0, 3 at P1,
1 at P2.**

### Block D — Reporting and follow-up *(4 articles)*

Issue the audit report · track open findings · your audit history · export for an external audit.
**0 at P0, 3 at P1, 1 at P2.**

**Set total: 22 articles · 9 at P0 · 9 at P1 · 4 at P2.**

---

## What happens next

| Outcome | Measure | Target |
|---|---|---|
| Audits complete offline without data loss | Sync failures; incomplete audits | Approaching zero |
| Checklists complete with no unanswered mandatory items | `BRU-QMS-01` breaches | **Zero** |
| Findings reach CAPA quickly | Finding-to-CAPA cycle | **Under 5 days** (`SP-029`) |
| Audit plan completes | `KPI-068` internal audit plan completion | **100%** |

**`PS-30`: articles 6, 8 and 12 carry this set.** Offline confidence, the mandatory-item block, and
the sync check. An audit lost to a sync failure is an audit that has to be repeated, and a branch
that has already been disrupted once.

---

## If it does not work

| Symptom | Cause | What to do |
|---|---|---|
| Audits repeated after sync loss | Article 12 not reaching auditors at the moment they leave | In-app prompt, not a help page |
| Mandatory items skipped | The block message is unclear, or the item is genuinely unanswerable at that site | Check `UI-021` first; then the checklist design |
| Classification varies between auditors | **Not a help failure** — calibration lapsed | `TR-016` §3.2; do not add a classification guide here (`PS-29`) |
| Safety findings queued rather than escalated | Article 17 buried in Block C | Promote it; safety routing is immediate |

---

## Related

`UI-021` · [`../../08_Training_and_Enablement/08B_Course_Packs/TR-016_Course_Pack_Quality_and_Field_Auditor.md`](../../08_Training_and_Enablement/08B_Course_Packs/TR-016_Course_Pack_Quality_and_Field_Auditor.md) ·
[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) · [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-032_Operational_Checklist_Library.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-032_Operational_Checklist_Library.md) ·
[`HC-004_Help_Set_P02_Technician_App.md`](HC-004_Help_Set_P02_Technician_App.md) · [`HC-011_Help_Set_P09_Logistics_and_Rider_App.md`](HC-011_Help_Set_P09_Logistics_and_Rider_App.md) — the same offline-first pattern · `LG-022` quality policy.

---

## Feedback

In-app helpfulness, capturable offline and replayed on sync. Reported with audit completion and
sync telemetry.

---

## Coverage and Authoring Plan *(addition)*

| Item | Position |
|---|---|
| Articles required | **22** · written **0** |
| Effort | 22 × 2–3 h = **45–65 hours** |
| Sequencing | Articles 6, 8, 12 (`PS-30`), then 9 P0 before W5 |
| Delivery | **In-app and offline** |
| Bengali | All 22 |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The audience is not a registered role** (`TR-002` `O-05`, `AUDIT-009` TR-07). Help can be published to them; they cannot be systematically assigned or tracked | MDM with Quality Manager | **W5** |
| **O-02** | **Offline help delivery inside `P11` must exist at W5** — the third file to record this gap after `HC-004` `O-01` and `HC-011` `O-02` | CTO with Content Design | **W5** |
| **O-03** | `TR-016` `O-01` records that the calibration case set does not exist. **`PS-29` depends on calibration existing elsewhere**; if it does not, classification consistency has no owner at all | Quality Manager | W5 |
| **O-04** | Clause-referenced checklists (`SP-032`, `LG-022`) must exist before Block A article 4 can be written | Quality Manager | W5 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Help_Article.md` at set level; additions justified
- [x] **Classification guidance kept in `TR-016` and not duplicated here (`PS-29`, `CP-01`)**
- [x] 22 articles enumerated with type and priority
- [x] The three articles carrying the set identified (`PS-30`)
- [x] The unregistered-role status of the audience carried forward, not silently assumed away
- [x] All internal links resolve
- [x] `BRU-QMS-01`/`-02` cited to `05-05`; `KPI-068` to `06-02`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 22 articles authored — outstanding**
- [ ] **`O-01` unregistered audience — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and Quality Manager**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
