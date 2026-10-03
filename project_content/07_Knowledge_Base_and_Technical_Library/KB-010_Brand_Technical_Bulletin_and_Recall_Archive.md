---
id: KB-010
title: Brand Technical Bulletin and Recall Archive
project: 1000FiX ERP System v2.0
content_type: Knowledge article
template: TPL_Knowledge_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-16
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Quality with Technical
author: Technical Library Owner with Quality Manager and Warranty Claims Officer
reviewers: [Technical Director, Legal Counsel, HSE Lead, Knowledge Manager, Account Management, Localisation Lead, CTO]
approver: Quality Manager with Legal Counsel
content_class: C
purpose: >
  The archive and handling standard for every technical bulletin, service notice and recall
  notification received from a brand partner — receipt, classification, linkage to affected models
  and parts, distribution to affected technicians, acknowledgement tracking, and routing of recalls
  out of the knowledge system into execution. P08 allows brands to push bulletins and recalls to
  1000FiX; failing to act on a recall notice is a serious liability, and a bulletin that arrives and
  reaches nobody is indistinguishable from one that never arrived.
traces_to: [M61, M09, M01, M40, M23, P08, P02, P03, MD-017, MD-021, MD-022, KB-001, KB-002, KB-003, KB-008, KB-009, KB-011, KB-015, SP-014, SP-029]
priority: P1
wave: W4
bilingual: yes
bn_counterpart: KB-010_Brand_Technical_Bulletin_and_Recall_Archive_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §5.4 FR-KMS-034 bulletin receipt classification distribution and acknowledgement; §8.2 bulletin lifecycle RECEIVED→CLASSIFIED→LINKED→DISTRIBUTED→ACKNOWLEDGED→ACTIONED→CLOSED
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §9 BRU-KMS-14 bulletins distributed to every affected technician with acknowledgement tracked; BRU-KMS-15 a recall notice is routed to M09 and M01 for execution and is never actioned within M61
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §11 AUT-KMS-12/13/14 — classification and distribution automation, recall routing, unacknowledged escalation; §12.4 INT-KMS-02 bulletin feeds and INT-KMS-03 recall channels
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §15 KPI-C61-11 — bulletins acknowledged by affected technicians within the declared period, 90% at W7 and 100% at W9
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P08 brand partner portal allows brands to push bulletins and recall notifications
    verified: 2026-08-16
    class: P1
supersedes: none
review_due: 2027-02-16
---

# KB-010 — Brand Technical Bulletin and Recall Archive

| Item | Value |
|---|---|
| Article type | **Bulletin** |
| Device family | All — scoped per bulletin |
| Brand / model scope | Every brand partner in `MD-017`; the register states the "17+" figure is itself unverified — see §1 |
| Skill level required | L1 to read and acknowledge · Technical Library Owner to classify · Quality Manager to close |
| Offline pack member | **Yes — mandatory.** A safety bulletin that only exists online has not been distributed |
| Review due | 2027-02-16 |

> **Template conformance.** Bulletin-type article — one of the four types the
> `TPL_Knowledge_Article.md` header declares. All sections retained in order and answered at
> archive level; §11–§13 are justified additions.

---

## 1. Purpose and Scope

**Two things arrive from brand partners and they must never be treated the same way.**

| Inbound | What it is | What 1000FiX must do | Owned by |
|---|---|---|---|
| **Technical bulletin / service notice** | Updated guidance, revised procedure, superseded part, known defect, firmware advisory | Classify, link, distribute, track acknowledgement, revise affected articles | `M61` — **this file** |
| **Recall notification** | The brand is withdrawing or remediating units in the field | Classify, link, distribute, **and route out of the knowledge system into campaign execution** | `M61` receives; **`M09` and `M01` execute** (`M61` §9 `BRU-KMS-15`) |

**`M61` §9 `BRU-KMS-15` is unambiguous: a recall notice is never actioned within `M61`.** The
knowledge system's job on a recall is to recognise it, link it, distribute it, and hand it to the
functions that can contact customers, hold devices and reimburse work. A knowledge base that
attempts to run a recall will do it invisibly and incompletely.

**In scope:** receipt channels; classification; linkage to models, faults and parts; distribution
and acknowledgement; the recall handover; archive structure and retention; the effect of a bulletin
on existing articles, mappings and notes; and the escalation ladder for unacknowledged bulletins.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Executing a recall campaign — customer contact, device hold, remediation, reimbursement | `M09` · `M01` · `BRU-KMS-15` |
| The brand relationship, authorisation scope and agreement terms | `M40` · `M08` · [`../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md) |
| Manuals and diagrams held as library content | [`KB-003_Repair_Manual_Index_and_Source_Register.md`](KB-003_Repair_Manual_Index_and_Source_Register.md) |
| Defects 1000FiX discovers itself | [`KB-011_Known_Issue_and_Workaround_Register.md`](KB-011_Known_Issue_and_Workaround_Register.md) — **the distinction is who found it** |
| Warranty claim submission and reconciliation | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md) |
| Internal non-conformance and CAPA | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) · `M23` |

> **A data caution carried forward.** `MD-017` records that audit `00-07` H2-12 flagged the
> **"17+ brands" figure as unverified** while an `M22` control depends on it. This archive's
> completeness measure (§11) is expressed as a proportion of brands *with an established bulletin
> channel*, not as a proportion of "17", precisely so that it does not silently inherit an
> unverified denominator.

---

## 2. Safety

> ⛔ **DANGER — an unactioned safety recall.** A recall exists because the manufacturer has
> concluded that units in the field can injure people (hazard). A recall notice that is received
> and not distributed, or distributed and not acknowledged, leaves devices in customers' homes and
> businesses that the manufacturer has already judged unsafe (consequence). **Every recall is
> classified within the receipt window, routed to `M09` and `M01` the same day, and distributed to
> every affected technician with acknowledgement tracked to 100%** (avoidance).

> ⚠ **WARNING — a technician working from superseded guidance.** A bulletin often exists because
> the original procedure was wrong or unsafe (hazard). A technician following the superseded
> article can be injured or can leave a device unsafe (consequence). **A bulletin that supersedes a
> procedure triggers immediate article revision or suspension, not a queued review** (avoidance) —
> `BL-09`.

> **NOTICE — legal and commercial exposure.** Failing to act on a recall notification is a serious
> liability and can put the brand authorisation itself at risk. `CG-013` legal escalation applies
> to any recall whose handling is in doubt.

---

## 3. Symptoms — *Bulletin article: the signals that this archive is failing*

| Signal | What it indicates |
|---|---|
| A technician learns of a bulletin from the customer or from the brand's public site | The receipt channel is not working, or distribution is not reaching the bench |
| Acknowledgement rate plateaus below 100% | Distribution reaches devices but not people, or the acknowledgement mechanism is being clicked without reading |
| A bulletin is received and the affected-model list is empty | Linkage failed; the bulletin was archived rather than applied |
| Claims are rejected citing a procedure superseded by a bulletin | The bulletin did not reach article revision (`BL-09`) |
| A recall is discovered during a service visit rather than before it | The recall was not linked to the device registry |
| A brand asks for our acknowledgement record and we cannot produce it | The archive is not evidential |
| Bulletins arrive only from brands with a `P08` portal presence | Channel coverage gap — see §11 |

---

## 4. Likely Causes

| # | Cause | Frequency | Confirming test |
|---:|---|---|---|
| 1 | No established channel with that brand | **Highest early** | `MD-017` channel status per brand |
| 2 | Bulletin received by an individual's email, not by the archive | High | Compare personal inboxes against archive entries during audit |
| 3 | Affected-model list not resolvable to `MD-021` codes | High | Linkage completeness per bulletin |
| 4 | Distribution targeted by branch rather than by competence and assignment | Medium | Distribution list vs affected-technician computation |
| 5 | Acknowledgement treated as a notification dismissal | Medium | Time-to-acknowledge distribution — near-zero times are a signal |
| 6 | Bulletin classified as informational when it supersedes a procedure | Medium | Article revision rate after bulletins |
| 7 | Recall arrives through a consumer channel rather than a partner channel | Medium | Source of first knowledge |

---

## 5. Diagnostic Procedure — *Bulletin article: the receipt-to-closure sequence*

`M61` §8.2 defines the lifecycle. This file states what happens at each transition and who owns it.

| State | Owner | Action | Gate to leave |
|---|---|---|---|
| **RECEIVED** | Technical Library Owner | Log source, brand, brand's own reference, date received, original document to `M24` | Logged within **1 working day** (`BL-01`) |
| **CLASSIFIED** | Technical Library Owner with Quality Manager | Assign type (§6.1) and severity (§6.2) | **Recall classification within the same working day** (`BL-02`) |
| **LINKED** | Technical analyst | Resolve affected models (`MD-021`), parts (`MD-022`), fault codes (`MD-024`), serial ranges | Linkage complete or explicitly recorded as unresolvable (`BL-04`) |
| **DISTRIBUTED** | System | Compute affected technicians from competence, certification and assignment; push to `P02` including the offline pack; notify branches | Distribution list computed, not hand-picked (`BL-05`) |
| **ACKNOWLEDGED** | Each technician | Confirm receipt and understanding | Tracked to 100%; escalation ladder in §10 (`BRU-KMS-14`) |
| **ACTIONED** | Varies by type | Article revision, mapping supersession, part-note change — **or, for a recall, handover to `M09`/`M01`** | Every affected artefact updated (`BL-09`) |
| **CLOSED** | Quality Manager | All actions complete, acknowledgement complete, evidence retained | Closure recorded with evidence |

**`BL-03`: a bulletin is never closed on the basis of distribution alone.** Distribution is a
system event. Closure requires that the affected articles, mappings and notes have actually
changed, and that acknowledgement is complete.

---

## 6. Repair Procedure — *Bulletin article: classification, linkage and handover*

### 6.1 Bulletin types

| Type | Definition | Distribution | Article effect | Routing |
|---|---|---|---|---|
| `technical_bulletin` | Revised procedure, technique or specification | Affected technicians | **Revise affected articles** | Stays in `M61` |
| `service_notice` | Operational change — parts, claim process, tooling, software | Affected technicians + R28 + Inventory | Revise notes and mappings | Stays in `M61` |
| `firmware_advisory` | Firmware issue, update or rollback guidance | Affected technicians + `M05` MSP team where relevant | Revise articles and `KB-008` mappings | Stays in `M61` |
| `parts_notice` | Supersession, withdrawal, counterfeit warning, availability | Affected technicians + Inventory + Procurement | Revise `KB-009` notes and `MD-022` | Stays in `M61`; `MD-022` change is MDM's |
| `safety_notice` | A hazard identified, short of a recall | **All technicians in the family, not only the certified** | Revise safety blocks; HSE approval | Stays in `M61`; HSE informed |
| **`recall`** | **Manufacturer withdrawal or mandatory remediation of units in the field** | **All technicians, all branches, contact centre, account management** | Revise articles **and hand over** | **`M09` + `M01` — `BRU-KMS-15`** |

### 6.2 Severity and response windows

| Severity | Definition | Classify within | Distribute within | Acknowledgement target |
|---|---|---|---|---|
| **S1 — Safety / recall** | Personal injury risk, or a manufacturer recall | **Same working day** | **Same working day** | **100% within 48 hours** |
| **S2 — Compliance / warranty** | Affects claim validity, statutory compliance or contractual obligation | 1 working day | 2 working days | 100% within 7 days |
| **S3 — Technical** | Revised procedure or specification | 2 working days | 5 working days | 90% within 14 days, 100% within 30 |
| **S4 — Informational** | Awareness only, no action required | 5 working days | Next scheduled digest | Acknowledgement optional; **read-tracking still recorded** |

**`BL-06`: severity is assigned by 1000FiX, not inherited from the brand's own label.** A brand may
label a notice "informational" for its own reasons. If it affects a procedure our technicians
follow, it is at least S3 here.

### 6.3 Linkage requirements

| Link | Bound to | Required | Purpose |
|---|---|:--:|---|
| Brand | `MD-017` `brand_code` | ✔ | Scoping and channel accountability |
| Affected models | `MD-021` `model_code` | ✔ | Distribution targeting and device-registry matching |
| Serial or batch range | Free text + structured where the brand supplies it | Where stated | **Recall targeting depends on it** |
| Affected parts | `MD-022` `part_code` | Where relevant | Stock quarantine and `KB-009` notes |
| Affected fault codes | `MD-024` | Where relevant | `KB-008` mapping supersession (`FC-12`) |
| Affected articles | `KNW-` codes | ✔ where any exist | `BL-09` revision trigger |
| Superseded bulletins | `BUL-` codes | Where applicable | Chain integrity |

**`BL-04`: a bulletin whose affected models cannot be resolved is not silently archived.** It is
recorded as `linkage_unresolved`, escalated to the brand for clarification, and **still distributed**
at its severity — an unresolvable link is a reason to widen distribution, not to narrow it.

### 6.4 Distribution targeting

**`BL-05`: the distribution list is computed, never hand-picked.**

| Input | Source |
|---|---|
| Technicians competent on the affected family | `MD-010` |
| Technicians certified for the brand | `MD-011` |
| Technicians with assignment history on the affected models | `M01`, `M31` |
| Branches holding affected stock | `M15` |
| Contact centre and account management, for S1 and S2 | `P10`, `M07` |
| **All technicians in the family**, for `safety_notice` and `recall` | Deliberate over-distribution |

> **Over-distribution is the correct error for safety content.** A technician who receives a safety
> notice for a model they never touch loses thirty seconds. A technician who does not receive one
> for a model they do touch is the failure this archive exists to prevent.

### 6.5 Acknowledgement

| Rule | Detail |
|---|---|
| **`BL-07`** | Acknowledgement is an explicit confirmation of receipt **and understanding**, not a notification dismissal |
| **`BL-08`** | For S1, acknowledgement includes a comprehension check — a single question drawn from the bulletin. A tick box confirms nothing |
| Offline | Acknowledgement captured offline replays exactly once on reconnection (`M61` T-08) |
| Evidence | The acknowledgement record is **evidential** — it is what is produced to a brand, an auditor or a court |
| Target | `M61` KPI-C61-11: **90% at W7, 100% at W9** |
| Non-acknowledgement | Escalation ladder in §10; `M61` AUT-KMS-14 escalates to branch manager and workshop supervisor |

### 6.6 The recall handover

**This is the most important procedure in this file and the one that must never be improvised.**

| Step | Who | Action | Never |
|---:|---|---|---|
| 1 | Technical Library Owner | Classify as `recall` on receipt; **same working day** | Never hold for a scheduled review |
| 2 | Technical Library Owner | Notify Quality Manager, Warranty Claims Officer (R28), Operations Director and Legal Counsel | Never route through one person |
| 3 | Technical analyst | Link affected models, serial ranges, parts | Never leave the range unrecorded because it is hard |
| 4 | System | **Route to `M09` and `M01`** for campaign execution (`BRU-KMS-15`, `M61` AUT-KMS-13) | **Never execute the recall inside `M61`** |
| 5 | System | Distribute to all technicians and branches; acknowledgement tracked at S1 | Never distribute selectively |
| 6 | `M09`/`M01` | Identify affected devices in the registry (`M17`), contact customers, hold and remediate | — |
| 7 | Quality Manager | Track the campaign to completion; the bulletin is not `CLOSED` until the campaign is | Never close on distribution (`BL-03`) |
| 8 | Technical Library Owner | Revise or suspend every affected article (`BL-09`) | — |
| 9 | Quality Manager with Legal | Retain the complete evidence chain | Never rely on email as the record |

**`BL-10`: a device covered by an open recall that presents for unrelated service is flagged at
intake.** The recall does not wait for the customer to respond to a campaign letter — the moment the
device is in our hands is the cheapest and most certain opportunity to act on it. This requires the
recall linkage to reach `M17` and `M01`, which is why step 4 is a system route and not an email.

### 6.7 Effect on existing content

**`BL-09`: a bulletin that changes guidance triggers immediate content action, not a queued
review.**

| Bulletin effect | Content action | Deadline |
|---|---|---|
| Procedure superseded | Affected `KNW-` articles revised, or **suspended** if revision cannot be immediate | S1/S2: same day suspension. S3: 5 working days |
| Code meaning changed | `KB-008` mappings superseded on receipt (`FC-12`) | Same day |
| Part superseded, withdrawn or counterfeit-warned | `KB-009` notes revised; `MD-022` change raised with MDM; **stock quarantined where indicated** (`BRU-INV-07`) | Same day for safety; 5 days otherwise |
| Manual revised | New `LIB-` entry; old entry `superseded` (`KB-003` §13) | 5 working days |
| Defect confirmed by the brand | `KB-011` known-issue record updated with the brand's confirmation and permanent-fix status | 5 working days |
| Safety guidance changed | Safety blocks revised; **HSE re-approval** (`BRU-KMS-03`) | Same day |

> **Suspension is a real and preferred option.** Where a bulletin invalidates a procedure and the
> corrected procedure cannot be written the same day, the honest action is to suspend the article
> with a visible notice rather than leave known-wrong guidance published while a revision is
> drafted. `KB-015` §6 governs suspension.

---

## 7. Parts

Bulletins frequently concern parts. The archive's obligations:

| Situation | Action |
|---|---|
| Part superseded | `KB-009` supersession chain updated; `MD-022` `supersedes_part_code` raised with MDM (`PC-11` — the archive does not edit the master) |
| Part withdrawn | Stock quarantined (`BRU-INV-07`); Inventory and Procurement notified; `KB-009` note set to prohibit |
| Counterfeit warning | **Immediate S1 or S2**; stock inspected; supplier escalated to Procurement (`M16`, `M42`) |
| Part now required for a procedure | `KB-009` note and stock planning (`M43`) |
| Consignment part affected | Brand consignment is excluded from own-stock valuation (`BRU-INV-04`) and its handling is the brand's; coordinate, do not act unilaterally |
| Recalled part in stock | Quarantine and follow the brand's return instruction; **never fit** |

---

## 8. Verification and QC

| Test | Pass criterion | Recorded in |
|---|---|---|
| Bulletins logged within 1 working day of receipt | 100% (`BL-01`) | Weekly archive report |
| Recalls classified same working day | **100%** (`BL-02`) | Per recall |
| Severity assigned by 1000FiX, not inherited | 100% (`BL-06`) | Classification record |
| Linkage complete or explicitly `linkage_unresolved` | 100% (`BL-04`) | Weekly |
| Distribution lists computed, not hand-picked | 100% (`BL-05`) | System record |
| **Acknowledgement rate** | 90% W7 → **100% W9** (`KPI-C61-11`) | Per bulletin + monthly |
| S1 acknowledgement within 48 hours | 100% | Per bulletin |
| S1 comprehension check present | 100% (`BL-08`) | Per bulletin |
| Time-to-acknowledge distribution inspected for implausibly fast responses | Reviewed monthly | Acknowledgement analytics |
| Affected articles revised or suspended within the deadline | 100% (`BL-09`) | Content change log |
| Recalls routed to `M09`/`M01` and never executed in `M61` | 100% (`BRU-KMS-15`) | Routing record — **negative test at UAT (`M61` AC-11)** |
| Recalled devices flagged at intake | 100% of presentations (`BL-10`) | Intake record |
| Bulletins closed only with evidence complete | 100% (`BL-03`) | Closure record |
| Offline pack carries current S1/S2 bulletins | 100% | Pack telemetry |

---

## 9. Resolution Coding

A bulletin carries no `MD-025` resolution code. It affects coding downstream:

| Effect | Detail |
|---|---|
| Recall remediation work | Coded on the service order created by `M01`, linked back to the `BUL-` reference |
| Work performed under a bulletin's revised procedure | Ordinary `RES-` coding; the article version in force is the audit trail |
| Claims citing a bulletin | `SP-014`; the bulletin reference strengthens the claim and is retained as evidence (`BRU-WTY-01`) |
| Rework caused by superseded guidance | Coded as rework (`BRU-SRM-06`) and attributed to the content failure, not to the technician — **`BL-09` exists so that this attribution is rare** |

---

## 10. Escalation

| Escalate when | To | Within |
|---|---|---|
| **A recall is received** | Quality Manager, R28, Operations Director, Legal Counsel — simultaneously | **Same working day** |
| A recall's affected range cannot be resolved | Brand partner via `P08` **and** widen distribution (`BL-04`) | Same day |
| S1 acknowledgement below 100% at 48 hours | Branch manager and workshop supervisor (`M61` AUT-KMS-14) | Immediately |
| S1 acknowledgement still incomplete at 5 days | Operations Director; **consider suspending the technician's assignment to that family** | Day 5 |
| A bulletin supersedes a procedure that cannot be revised same-day | **Suspend the article** (`KB-015` §6); Knowledge Manager | Same day |
| A bulletin arrives outside the archive — personal email, chat, verbal | Technical Library Owner; log it and fix the channel | Same day |
| A brand has no established bulletin channel | Account Management and `M40`; recorded as a channel gap (§11) | Monthly review |
| We learn of a recall from a public or consumer source first | **Quality Manager and Legal Counsel** — this is a channel failure with liability implications | Same day |
| A counterfeit-part warning is received | Quality Manager, Inventory Manager, Procurement | Same day |
| Any doubt about the handling of a recall | **Legal Counsel — `CG-013` escalation trigger** | Same day |

---

## 11. Archive Structure, Retention and Coverage *(addition — justified: the archive is evidential and its retention and completeness measures have no home in the template)*

### 11.1 Record structure

| Column | Type | Req | Notes |
|---|---|:--:|---|
| `bulletin_code` | `BUL-nnnnn` | ✔ | Permanent, never reused |
| `brand_code` | fk → `MD-017` | ✔ | |
| `brand_reference` | text(80) | ✔ | The brand's own number — **kept distinct from ours** |
| `bulletin_type` | enum | ✔ | §6.1 |
| `severity` | enum | ✔ | §6.2, assigned by 1000FiX (`BL-06`) |
| `received_at`, `received_via`, `received_by` | | ✔ | Channel accountability |
| `document_ref` | fk → `M24` | ✔ | The original, unaltered |
| `affected_models`, `affected_parts`, `affected_fault_codes` | multi-fk | ✔ / conditional | §6.3 |
| `serial_range` | text | conditional | **Required for recalls where the brand supplies it** |
| `linkage_status` | enum | ✔ | complete / `linkage_unresolved` |
| `affected_articles` | multi-fk → `KNW-` | ✔ where any | `BL-09` |
| `distribution_computed_at`, `distribution_count` | | ✔ | `BL-05` |
| `acknowledgement_target`, `acknowledged_count` | | ✔ | `KPI-C61-11` |
| `routed_to` | enum | conditional | `M09` / `M01` for recalls (`BRU-KMS-15`) |
| `campaign_ref` | fk | conditional | The executing campaign |
| `state` | enum | ✔ | `M61` §8.2 lifecycle |
| `closed_at`, `closed_by`, `closure_evidence_ref` | | conditional | `BL-03` |
| `supersedes_bulletin_code` | fk | | Chain |

### 11.2 Retention

| Item | Retention | Basis |
|---|---|---|
| The bulletin document itself | Per `M24` retention policy; **never shorter than the affected models' service life** | Evidential |
| Acknowledgement records | **Retained as long as the bulletin** | This is the evidence produced to a brand or an auditor |
| Recall campaign linkage and outcome | Per `M09` and legal retention | Liability |
| Superseded bulletins | Archived, never deleted (`CP-10`) | Chain integrity |

### 11.3 Coverage measures

| Measure | Definition | Why expressed this way |
|---|---|---|
| **Channel coverage** | Brands in `MD-017` with an established, tested bulletin channel ÷ brands in `MD-017` | **Not "÷ 17"** — the 17+ figure is recorded as unverified in `MD-017` and `00-07` H2-12 |
| Channel liveness | Brands from which at least one bulletin has been received in 12 months | A channel that has never delivered anything is not established |
| Acknowledgement rate | `KPI-C61-11` | |
| Time from receipt to distribution, by severity | Against §6.2 windows | |
| Articles revised per bulletin | Tests whether `BL-09` is real | |
| Recalls where we were not the first to know | **Target zero** | The clearest single indicator of channel health |

---

## 12. Related Documents *(addition — justified: category convention)*

| Document | Relationship |
|---|---|
| [`KB-003_Repair_Manual_Index_and_Source_Register.md`](KB-003_Repair_Manual_Index_and_Source_Register.md) | Bulletins revise manuals; both registers cross-reference |
| [`KB-008_Fault_Code_Library_and_Interpretation_Guide.md`](KB-008_Fault_Code_Library_and_Interpretation_Guide.md) | `FC-12` — a bulletin supersedes a mapping on receipt |
| [`KB-009_Parts_Compatibility_and_Substitution_Notes.md`](KB-009_Parts_Compatibility_and_Substitution_Notes.md) | Parts notices revise substitution notes |
| [`KB-011_Known_Issue_and_Workaround_Register.md`](KB-011_Known_Issue_and_Workaround_Register.md) | **The mirror image** — this file is what the brand tells us; that file is what we found ourselves |
| [`KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md`](KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md) | Suspension mechanism used by `BL-09` |
| [`KB-016_Technician_Field_Reference_Card_Set.md`](KB-016_Technician_Field_Reference_Card_Set.md) | S1/S2 bulletins in the offline pack |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md) | Claims citing bulletins |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) | Bulletin handling is auditable under the internal audit programme |
| [`../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md) | Brand codes, authorisation scope, and the unverified "17+" note |
| `M09` Warranty, Protection Plans and Claims · `M01` Service Request and Order Management | **The recall executors** |
| `M17` Device and Customer Asset Registry | Recall-to-device matching for `BL-10` |
| `LG-013` Service Terms, Warranty Terms and Exclusions · `LG-024` Regulatory Disclosure and Statutory Notice Register | The nearest registered legal artefacts. **Neither covers product safety or recall handling** — see `O-05` and audit finding **KB-03** |
| `TR-016` Course Pack — Quality and Field Auditor · `TR-009` Field Technician | Train receipt handling and acknowledgement |

---

## Sources and Currency

| Source | Verified | Next review |
|---|---|---|
| `M61` §5.4 FR-KMS-034; §8.2 bulletin lifecycle; §9 `BRU-KMS-14`, `BRU-KMS-15`; §11 AUT-KMS-12/13/14; §12.4 INT-KMS-02/03; §15 `KPI-C61-11`; §17 AC-11/AC-12 | 2026-08-16 | 2027-02-16 |
| `04-00` `P08` — brands push bulletins and recall notifications | 2026-08-16 | 2027-02-16 |
| `05-05` §2 `BRU-WTY-01`; `BRU-INV-04`, `BRU-INV-07`; `BRU-SRM-06` | 2026-08-16 | 2027-02-16 |
| `MD-017` — brand register; audit `00-07` H2-12 records the "17+ brands" figure as unverified | 2026-08-16 | 2027-02-16 |
| `MD-021`, `MD-022`, `MD-024` — linkage targets | 2026-08-16 | 2027-02-16 |

> **No specific brand, bulletin or recall is named in this file.** The archive holds those; the
> standard governs how. Naming a live recall in a governing document would date it and would put an
> unmaintained copy of a safety notice into circulation alongside the maintained one.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The wave placement is a genuine risk.** `KB-010` is `P1`/`W4`, and `M61` — which implements bulletin receipt, distribution and acknowledgement — is `W6`. **Brand relationships and recalls exist from day one.** Until both land, bulletin handling is a manual process with no system support and no acknowledgement tracking, and the liability in §2 is live throughout | Quality Manager with Operations Director and CTO | **W1 — an interim manual procedure is needed now, not in W4** |
| **O-02** | **Bulletin channels are not established with most brands.** `M40`, which owns the brand relationship, lands at W7 — later than both this file and `M61`. Channel establishment cannot wait for it | Account Management with Quality Manager | **W2 — start with the highest-volume brands** |
| **O-03** | The `MD-017` "17+ brands" figure remains unverified (`00-07` H2-12). §11.3 avoids depending on it, but the register itself still needs closing | Commercial with MDM | W4 |
| **O-04** | The comprehension check for S1 acknowledgement (`BL-08`) has no authoring standard. One question per bulletin, written by whom, reviewed by whom, in two languages | Knowledge Manager with L&D | W4 |
| **O-05** | **No registered `LG` file covers product safety or recall handling.** The 24-row `LG` register was checked row by row during authoring: `LG-013` is Service Terms and Warranty Exclusions, `LG-014` is Refund/Cancellation/Compensation, `LG-024` is Regulatory Disclosure. None addresses recall liability, customer notification obligations, or the company's duty on receipt of a manufacturer recall. **This content file is therefore carrying a legal obligation with no legal artefact behind it.** Raised as audit finding **KB-03** | Legal Counsel with Programme Content Lead | **W4 — and the exposure is live from W1** |
| **O-06** | `BL-10` — flagging a recalled device at intake — requires recall linkage to reach `M17` and `M01`. Whether that path exists is unconfirmed | CTO with Technical Director | Before W4 |
| **O-07** | Bengali counterpart and the bilingual handling of brand documents. Brand bulletins arrive in English; the **acknowledgement and the action instruction must be readable in Bengali**, even where the source is not translated | Localisation Lead with Quality Manager | W4 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Knowledge_Article.md` as a Bulletin-type article; additions §11–§12 justified
- [x] Bulletin and recall separated, with the `BRU-KMS-15` prohibition on executing recalls in `M61` stated as a rule and as a negative test
- [x] Lifecycle mapped to `M61` §8.2 with owners and gates at every transition
- [x] Severity assigned by 1000FiX, not inherited from the brand (`BL-06`)
- [x] Distribution computed, not hand-picked, with deliberate over-distribution for safety content
- [x] Acknowledgement defined as confirmation of understanding, with a comprehension check at S1
- [x] Content-revision obligations bound to bulletin receipt, with suspension as a legitimate action
- [x] Recall handover written as a numbered sequence with explicit "never" column
- [x] Recalled-device-at-intake rule stated (`BL-10`)
- [x] Coverage measures avoid the unverified "17+" denominator
- [x] All internal links resolve
- [x] `BRU-KMS-*` cited to `M61` §9; `BRU-WTY-*`, `BRU-INV-*`, `BRU-SRM-*` cited to `05-05`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` interim manual bulletin procedure for W1–W6 — outstanding; the liability is live now**
- [ ] **`O-05` legal cover for recall handling confirmed — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Quality Manager and Legal Counsel**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
