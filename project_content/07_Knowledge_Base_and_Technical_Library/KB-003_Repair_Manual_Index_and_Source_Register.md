---
id: KB-003
title: Repair Manual Index and Source Register
project: 1000FiX ERP System v2.0
content_type: Knowledge article
template: TPL_Knowledge_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-16
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Knowledge Manager with Legal
author: Technical Library Owner with Legal Counsel
reviewers: [Quality Manager, Technical Director, Legal Counsel, Finance Director, CTO, Localisation Lead]
approver: Quality Manager with Legal Counsel
content_class: C
purpose: >
  The register of every repair manual, service manual, wiring diagram, schematic, exploded view and
  parts diagram the company holds, with its source, its licensing status, its redistribution scope
  and its coverage gaps. Manuals carry copyright and brand-agreement constraints; an unmanaged
  library is a legal exposure that grows silently with every ingestion, and a technician who cannot
  tell whether we are permitted to hold a diagram will either not use it or use it unlawfully.
traces_to: [M61, M24, M40, M08, P02, P08, MD-017, MD-021, KB-001, KB-002, KB-010, LG-020]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: KB-003_Repair_Manual_Index_and_Source_Register_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §5.1 FR-KMS-004, FR-KMS-012, §6 T-13 — library entries indexed by brand and model, bulk manual ingestion, files stored in M24
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §9 BRU-KMS-16 — brand manuals and diagrams are used within the terms of the brand agreement and their redistribution is scoped accordingly
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §16.3 and §18 Q-03 — M40 lands in W7 after M61 in W6, so brand-agreement terms are not held as structured data when the library is built; licence terms recorded as free text on each entry as the interim control
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §4 — no third-party technical database covers the Bangladeshi mobile, appliance and IT device mix, so the library must be built and curated internally
    verified: 2026-08-16
    class: P1
  - source: Copyright Act 2023 (Bangladesh), which replaced the Copyright Act 2000 — protection for literary and artistic works subsists for the life of the author plus 60 years; unauthorised publication or distribution carries statutory penalties
    verified: 2026-08-16
    class: P1
    note: Legal Counsel must confirm the applicable sections and the fair-dealing scope before this register is relied on — see Open Item O-02
supersedes: none
review_due: 2027-02-16
---

# KB-003 — Repair Manual Index and Source Register

| Item | Value |
|---|---|
| Article type | **Reference** |
| Device family | All — `DF-IT`, `DF-HA`, `DF-MB`, `DF-SRV`, `DF-SEC` |
| Brand / model scope | All held brands; scoped per entry |
| Skill level required | L1 to read the register · Technical Library Owner to maintain · Legal Counsel to classify licence |
| Offline pack member | **Partially** — diagram extracts yes, full manuals no (§11) |
| Review due | 2027-02-16 |

> **Template conformance.** This is a **Reference**-type article, one of the four types the
> `TPL_Knowledge_Article.md` header table declares. All template sections are retained in order.
> Where a section has no procedural meaning for a register, it is answered at register level and
> the interpretation is stated in the heading — no section is removed (`CP-09`, `CG-008`).
> Sections 11–14 are additions, justified in §11.

---

## 1. Purpose and Scope

**In scope:** the register's record structure; how a manual or diagram enters it; the licence
classification scheme; the redistribution scope that flows from that classification onto every
article citing the entry; coverage measurement against `MD-021`; the gap and acquisition backlog;
and the retention and withdrawal rules.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Storage of the underlying file, versioning, retention, legal hold | `M24`; `M61` holds the entry, `M24` holds the file (`M61` §3.2) |
| The brand relationship and the agreement itself | `M40` Partner · `M08` Contract · [`../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md) |
| Bulletins, service notices and recalls received from brands | [`KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md`](KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md) |
| Articles written *from* a manual | [`KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md`](KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md) … [`KB-007_Troubleshooting_Guide_Set_Server_Network_and_CCTV.md`](KB-007_Troubleshooting_Guide_Set_Server_Network_and_CCTV.md) |
| Intellectual-property policy for content the company itself creates | **No registered `LG` file covers third-party IP or content licensing.** The nearest are `LG-020` Acceptable Use and Internal Access Policy (who may access what) and `LG-024` Regulatory Disclosure and Statutory Notice Register. This is a genuine gap — see `O-06` and audit finding **KB-02** |

**Why this file is `P2` but behaves like a legal control.** The register's priority reflects when
it is *needed* (W2, with the first offline packs). Its consequence is legal from the first
ingestion. `M61` §9 `BRU-KMS-16` makes brand-agreement compliance a hard rule; this register is
the only place where the terms are recorded against the artefact they govern.

---

## 2. Safety

> ⚠ **WARNING — wrong-manual risk.** A technician following a procedure from a manual for an
> adjacent model generation can apply the wrong torque, the wrong voltage, the wrong refrigerant
> charge or the wrong disassembly order (hazard). The consequences range from a destroyed board to
> a refrigerant release or a punctured lithium cell (consequence). **Every register entry states
> its exact model applicability, and an entry whose applicability cannot be established is marked
> `applicability: unverified` and is excluded from offline packs** (avoidance) — rule `LB-07`.

> **NOTICE — legal exposure.** Holding, indexing or redistributing a manual outside the terms of
> the brand agreement or outside fair dealing under the Copyright Act 2023 exposes the company to
> statutory penalty and to the loss of the brand authorisation on which warranty revenue depends.
> This is a property and commercial risk, not a personal-injury risk, and it is why the register
> carries a licence classification on every entry.

Safety data for the hazards a manual's procedures involve is held in
[`KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](KB-013_ESD_Chemical_and_Battery_Safety_Data.md);
this register does not restate it.

---

## 3. Symptoms — *Reference article: the signals that this register is failing*

| Signal | What it indicates | Where observed |
|---|---|---|
| A technician photographs a manual page and shares it in a private chat | The register is not findable, or does not hold the manual | `M61` usage analytics show zero opens against high job volume |
| The same model appears repeatedly in escalations with "no documentation" | A coverage gap (§8) | Escalation reasons |
| A brand queries how we obtained a document | A licence classification is wrong or absent | Brand correspondence, `P08` |
| Articles paste manual images inline | `AU-27` is being broken; redistribution scope is being bypassed | Article review |
| Offline pack size exceeds budget | Full manuals are being packed instead of extracts (§11) | Pack telemetry |
| An entry has no `licence_class` | Ingestion bypassed the classification gate | Weekly register conformance report |

---

## 4. Likely Causes

| # | Cause | Frequency | Confirming test |
|---|---|---|---|
| 1 | Manual acquired by an individual technician and never registered | **Most common** | Compare `LIB-` entries against models with job volume |
| 2 | Brand agreement silent on documentation rights | Common — `M61` Q-03 records this as unresolved | Read the agreement; if silent, classify `restricted_pending_confirmation` |
| 3 | Manual exists only for a market variant we do not service | Common in appliances | Compare manual model list against `MD-021` |
| 4 | Manual is behind a brand portal requiring per-technician credentials | Common | Check `INT-KMS-01` access route |
| 5 | No manual exists — grey-market or white-label device | Frequent in `DF-HA` and low-cost `DF-MB` | Manufacturer enquiry returns nothing |
| 6 | Manual held but not OCR-indexed, so search cannot find it | Occasional | `extracted_text_ref` empty |

---

## 5. Diagnostic Procedure — *Reference article: how to establish what we hold*

| Step | Action | Expected result | If not |
|---:|---|---|---|
| 1 | Resolve the device to a `model_code` in `MD-021` | A single model | Unresolved device — register it first (`MDL-01`) |
| 2 | Query the register by `model_code` | One or more `LIB-` entries | Go to step 4 |
| 3 | Check the entry's `licence_class` and `redistribution_scope` | `internal_use` or wider | If `restricted_pending_confirmation`, do not export; read on-platform only |
| 4 | Query by `parts_family_code` and by generation-adjacent models | A near-match, marked as such | Go to step 5 |
| 5 | Check the brand portal route (`INT-KMS-01`) | Acquirable | Raise an acquisition request (§6) |
| 6 | Record the gap against the model with its 90-day job volume | Gap enters the acquisition backlog | — |

---

## 6. Repair Procedure — *Reference article: acquisition, classification and ingestion*

### 6.1 Acquisition routes, in order of preference

| # | Route | Licence position | Typical coverage |
|---:|---|---|---|
| 1 | **Brand authorised-service-partner documentation portal** (`INT-KMS-01`) | Governed by the brand agreement; the strongest position | Authorised brands only |
| 2 | Manual supplied with a consignment or a service contract | Governed by that contract | Narrow, but unambiguous |
| 3 | Manufacturer public download (consumer or service manual published openly) | Publisher's own terms; usually internal use permitted, redistribution not | Broad for `DF-IT` |
| 4 | Paid third-party technical database subscription | Subscription terms; per-seat, no redistribution | `M61` §4 records that **none covers the Bangladeshi device mix**, so this is supplementary at best |
| 5 | Internally authored substitute — 1000FiX writes its own procedure and diagram | **Company-owned; no constraint** | The only route that scales for grey-market devices |
| 6 | Uncontrolled internet source | **Prohibited for registration** (`LB-04`) | — |

> **Route 5 is the strategic answer and route 6 is the one that will happen anyway.** For a large
> part of the Bangladeshi appliance and low-cost mobile market no lawful manual exists in any
> language. The register's job is to make that visible as a gap that route 5 fills, rather than
> letting it be filled invisibly by route 6.

### 6.2 Ingestion procedure

| Step | Who | Action | Gate |
|---:|---|---|---|
| 1 | Technical Library Owner | Record source, date, acquiring person and route | — |
| 2 | Technical Library Owner | Resolve model applicability against `MD-021`; mark `unverified` where it cannot be established | `LB-07` |
| 3 | **Legal Counsel or delegated Legal reviewer** | Assign `licence_class` and `redistribution_scope` per §6.3 | **Hard gate — no entry is published without a classification (`LB-01`)** |
| 4 | System | Store the file in `M24` content-addressed storage; the register holds only a reference (`M61` T-04) | `BRU-KMS-01` |
| 5 | System | OCR and text extraction (`INT-KMS-05`); index for search (`M61` FR-KMS-016) | Entry marked `unindexed` on failure, not blocked |
| 6 | Technical Library Owner | Produce the **diagram extract set** for offline use per §11 | `LB-09` |
| 7 | Technical Library Owner | Link the entry to affected `KNW-` articles and `TRE-` trees | `KB-001` §4.5 |
| 8 | System | Add to the coverage computation (§8) | — |

### 6.3 Licence classification scheme

**Every entry carries exactly one class.** The class determines what may be done with it, and it
propagates to every article that cites it (`KA-09`).

| Class | Meaning | May be read on-platform | May be in an offline pack | May be sent to a customer | May be shown to another brand |
|---|---|:--:|:--:|:--:|:--:|
| `company_owned` | 1000FiX authored it (route 5) | ✔ | ✔ | ✔ | ✔ |
| `brand_agreement` | Held under a named brand agreement clause | ✔ | ✔ | ✖ | ✖ |
| `publisher_open` | Publicly published by the manufacturer for end users | ✔ | ✔ | Link only, never the file | ✔ |
| `subscription` | Held under a paid per-seat subscription | ✔ (licensed seats only) | ✖ | ✖ | ✖ |
| `restricted_pending_confirmation` | Held, but the right to hold it is unconfirmed | ✔ (on-platform, watermarked, logged) | ✖ | ✖ | ✖ |
| `withdrawn` | Right to hold has lapsed or been withdrawn | ✖ | ✖ — **purged from packs** | ✖ | ✖ |

> **`restricted_pending_confirmation` is the honest default and it is deliberately usable.**
> `M61` §16.3 records that `M40` — which will hold the structured brand-agreement terms — lands a
> full wave *after* `M61`. Until then the terms are free text on the entry. A classification
> scheme that forced a binary lawful/unlawful decision on day one would either block the library
> or invite a fictional "yes". This class says: we hold it, we can read it internally with an
> access log, we will not redistribute it, and Legal owes us an answer.

### 6.4 Register record structure

| Column | Type | Req | Constraint | Description |
|---|---|:--:|---|---|
| `library_code` | char(9) | ✔ | `LIB-nnnnn`, permanent | Never reused |
| `entry_type` | enum | ✔ | service_manual / user_manual / wiring_diagram / board_schematic / exploded_view / parts_diagram / firmware_note / training_deck | |
| `title` | text(200) | ✔ | As published — do-not-translate | |
| `brand_code` | fk | | → `MD-017`; null for unbranded | |
| `model_codes` | multi-fk | ✔ | → `MD-021`, or `family_wide` | |
| `applicability` | enum | ✔ | verified / adjacent_generation / **unverified** | `LB-07` |
| `device_family_code` | fk | ✔ | → `MD-021` §2.1 | |
| `document_ref` | fk | ✔ | → `M24` content-addressed reference | Never a duplicate file |
| `page_count` | int | | | Payload planning |
| `extracted_text_ref` | fk | | → OCR output | Search index source |
| `language` | enum | ✔ | en / bn / other | Most OEM manuals are English only |
| `source_route` | enum | ✔ | §6.1 routes 1–5 | Route 6 cannot be recorded (`LB-04`) |
| `source_detail` | text(300) | ✔ | Portal, contract clause, URL, or author | Evidence under `CG-012` |
| `acquired_on` | date | ✔ | | |
| `acquired_by` | fk | ✔ | → employee | Accountability |
| `licence_class` | enum | ✔ | §6.3 | **Hard gate `LB-01`** |
| `licence_terms` | text(1000) | ✔ | Free text until `M40` lands | `M61` §16.3 interim control |
| `redistribution_scope` | enum | ✔ | internal_only / offline_pack / brand_visible / customer_visible | Propagates under `KA-09` |
| `review_due` | date | ✔ | Annual, or on agreement change | `KB-015` |
| `extract_set_ref` | fk | | → the diagram extract set | §11 |
| `status` | enum | ✔ | active / superseded / withdrawn | |

### 6.5 Governing rules

| # | Rule | Class |
|---|---|:--:|
| **LB-01** | No entry is published without a `licence_class` assigned by Legal | **H** |
| **LB-02** | The register holds entries; `M24` holds files. No file is stored twice (`M61` T-04, `BRU-KMS-01`) | **H** |
| **LB-03** | `redistribution_scope` propagates to every article citing the entry; an article can never widen it (`KA-09`) | **H** |
| **LB-04** | An uncontrolled internet source may not be registered. Where such a document is the only guidance available, it is used to *inform* an internally authored article (route 5) and is not itself held | **H** |
| **LB-05** | A `withdrawn` entry is purged from every offline pack and from the `M32` corpus within the propagation window (`BRU-KMS-05`) | **C** |
| **LB-06** | Manual pages are never pasted into an article; they are referenced (`AU-27`) | **H** |
| **LB-07** | An entry with `applicability: unverified` is readable on-platform with a visible warning and is excluded from offline packs | **H** |
| **LB-08** | `restricted_pending_confirmation` entries are watermarked and every open is logged | **C** |
| **LB-09** | Only the **diagram extract set** enters an offline pack, never the full manual (§11) | **H** |
| **LB-10** | Coverage gaps are ranked by 90-day job volume and published weekly as the acquisition backlog | **C** |
| **LB-11** | Every entry carries a named `acquired_by`; anonymous ingestion is not possible | **H** |
| **LB-12** | Licence classification is reviewed annually and on any change to the brand agreement | **C** |

---

## 7. Parts — *Reference article: not applicable*

No parts are consumed by a register. The nearest equivalent — the parts diagrams a manual
contains — are themselves `LIB-` entries of `entry_type: parts_diagram`, and the part records they
depict are governed by
[`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md)
and [`KB-009_Parts_Compatibility_and_Substitution_Notes.md`](KB-009_Parts_Compatibility_and_Substitution_Notes.md).

---

## 8. Verification and QC

| Test | Pass criterion | Recorded in |
|---|---|---|
| Every entry carries a `licence_class` | 100% | Weekly register conformance report |
| Every entry carries `licence_terms` text until `M40` lands | 100% | Weekly |
| No duplicate files between the register and `M24` | Zero duplicates by content hash | Storage audit |
| Model applicability resolves in `MD-021` | 100%, or explicitly `unverified` | Weekly |
| OCR indexed | > 95% of entries searchable by content | Index report |
| Offline packs contain no full manuals | Zero (`LB-09`) | Pack telemetry |
| `withdrawn` entries absent from packs and `M32` corpus | Zero within the propagation window | Propagation test (`M61` AC-04) |
| Coverage of models with ≥ 50 jobs / 12 months | Rising; target set at first measurement | Monthly coverage report |
| `restricted_pending_confirmation` count and age | **Falling**; nothing older than 12 months | Monthly to Legal |

---

## 9. Resolution Coding — *Reference article: not applicable*

A register entry is not a repair outcome and carries no `MD-025` resolution code. Articles derived
from a manual carry their own coding under `AU-13`.

---

## 10. Escalation

| Escalate when | To | With what evidence |
|---|---|---|
| A brand disputes our right to hold a document | Legal Counsel, then Quality Manager and the brand relationship owner | Entry record, `source_detail`, `licence_terms`, access log |
| A brand issues a withdrawal notice | Technical Library Owner → immediate `withdrawn` status; Legal informed | Notice, propagation confirmation |
| An entry has been `restricted_pending_confirmation` for more than 12 months | Legal Counsel with Finance Director | Age report |
| A high-volume model has no manual and route 5 authoring is not resourced | Technical Director → Ops Director | Gap report with job volume |
| A manual page is found pasted into an article | Quality Manager; article returned to `Draft` | Article version |
| A technician is found sharing manual pages outside the platform | Line manager + Quality Manager; treated as a policy matter, not a disciplinary default | Usage log |
| Legal cannot classify because the agreement is silent (`M61` Q-03) | Finance Director / Legal, as `M61` assigns it | The agreement text |

---

## 11. Offline Extract Sets *(addition — justified: the offline pack rule has no home in the template and is the single largest payload decision in `P02`)*

`M61` T-02 records that diagrams are both the largest payload and the most valuable content, and
that the sync strategy is a genuine engineering problem. `LB-09` resolves the content half of it.

| Rule | Detail |
|---|---|
| What enters a pack | A curated **extract set** — the specific diagram pages, pinouts, connector maps and exploded views a technician needs at the bench |
| What never enters a pack | The full manual. A 400-page service manual for one model would consume a technician's entire budget |
| Who curates | Technical Library Owner with an R12 specialist for that family |
| Format | Image or vector extract at device-appropriate resolution, with the source `LIB-` code stamped on every page |
| Licence | Inherits the parent entry's class; `subscription` and `restricted_pending_confirmation` **never** extract |
| Currency | An extract set is versioned with its parent; a withdrawn parent purges its extracts (`LB-05`) |
| Budget | Governed by the per-device storage budget — **undecided**, see `O-01` |

---

## 12. Coverage and the Acquisition Backlog *(addition — justified: `LB-10` requires a published backlog and the ranking method must be stated)*

| Rank input | Weight | Source |
|---|---|---|
| 90-day job volume for the model | Primary | `M01` |
| Escalation rate on that model | Secondary | `M31`, `M02` |
| Rework rate on that model | Secondary | `BRU-SRM-06` rework flags |
| Brand-warranty exposure | Modifier | `M09` claim volume |
| Whether route 1 access exists | Modifier — cheap acquisitions rank up | `INT-KMS-01` |

The backlog is published weekly alongside the article coverage backlog (`M61` AUT-KMS-09) so that
"we have no manual" and "we have no article" are seen as one problem with two remedies.

---

## 13. Retention, Withdrawal and Obsolescence *(addition — justified: `M24` owns file retention but the *entry* lifecycle is a knowledge decision)*

| Event | Entry action | File action (`M24`) |
|---|---|---|
| Model reaches end of service life in `MD-021` | Entry `superseded`; removed from packs; remains searchable | Retained to `M24` policy |
| Manufacturer publishes a revision | New entry; old entry `superseded` with a pointer | Both retained |
| Brand withdraws permission | Entry `withdrawn`; purged from packs and `M32` | **Legal instruction governs**; deletion only on Legal instruction |
| Subscription lapses | Entry `withdrawn`; seats revoked | Per subscription terms |
| Company-authored substitute exists | Original entry may be `superseded` in favour of `company_owned` | Retained |

**Never delete on the register's own authority.** `CP-10` archives superseded content rather than
deleting it, and a deletion that later turns out to have destroyed evidence of lawful acquisition
is worse than the storage cost of keeping it.

---

## 14. Related Documents *(addition — justified: category convention across `SP` and `MD` files)*

| Document | Relationship |
|---|---|
| [`KB-001_Knowledge_Architecture_and_Tagging_Standard.md`](KB-001_Knowledge_Architecture_and_Tagging_Standard.md) | `LIB-` object definition and facet binding |
| [`KB-002_Article_Template_and_Authoring_Standard.md`](KB-002_Article_Template_and_Authoring_Standard.md) | `AU-27` reference-don't-paste rule |
| [`KB-009_Parts_Compatibility_and_Substitution_Notes.md`](KB-009_Parts_Compatibility_and_Substitution_Notes.md) | Parts diagrams feed compatibility work |
| [`KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md`](KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md) | Bulletins amend manuals; the two registers cross-reference |
| [`KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md`](KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md) | Annual licence review under `LB-12` |
| [`../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md) | Brand codes and authorisation scope |
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md) | Model applicability |
| `LG-020` Acceptable Use and Internal Access Policy | Governs who may access `restricted_pending_confirmation` entries; **does not cover third-party IP licensing** — see `O-06` |
| `M24` Document, Records and E-Signature | File storage, retention, legal hold |
| `M40` Partner, Channel, Alliance and Franchise | Structured brand-agreement terms, from W7 |

---

## Sources and Currency

| Source | Verified | Next review |
|---|---|---|
| `M61` §5.1 FR-KMS-004 / FR-KMS-012, §6 T-04 / T-13, §9 `BRU-KMS-16`, §16.3, §18 Q-03 | 2026-08-16 | 2027-02-16 |
| `MD-017` brand register · `MD-021` model catalogue | 2026-08-16 | 2027-02-16 |
| Copyright Act 2023 (Bangladesh) — replaced the Copyright Act 2000; life + 60 years for literary and artistic works; statutory penalties for unauthorised publication or distribution | 2026-08-16 | **Legal Counsel to confirm applicable sections and fair-dealing scope — `O-02`** |
| `M61` §4 — no third-party technical database covers the Bangladeshi device mix | 2026-08-16 | 2027-02-16 |

> **Sourcing caution under `CG-012`.** The Copyright Act citation above establishes the general
> position only. **The register must not be relied on as a legal opinion.** `CG-013` triggers a
> legal escalation for any content carrying statutory consequence, and the licence classification
> gate (`LB-01`) is precisely that escalation made routine.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The per-device offline storage budget is undecided** (`M61` Q-04). Extract-set composition in §11 cannot be specified without it | CTO with Ops Director | Before W2 `P02` build |
| **O-02** | **Legal Counsel has not confirmed whether brand agreements permit 1000FiX to hold, index and redistribute manuals, and on what terms.** This is `M61` Q-03, assigned to Finance Director / Legal, and it is blocking for the technical library. `restricted_pending_confirmation` is the interim control, not the answer | Finance Director / Legal Counsel | **W6 — blocking** |
| **O-03** | No entries exist. This file is the register's specification; **the register is empty and its population is an acquisition programme**, not a build task (`M61` §16.4) | Technical Library Owner | Population begins W2, substantive by W6 |
| **O-04** | The Technical Library Owner position is unfilled (`KB-002` `O-01`); §6.2 assigns it eight steps of every ingestion | Quality Manager with HR Director | W5 |
| **O-05** | Route 5 — internally authored substitutes for grey-market devices — has no allocated authoring capacity, yet §6.1 identifies it as the only scalable answer for a large part of the Bangladeshi device mix | Technical Director with Ops Director | W4, before appliance and low-cost mobile volume peaks |
| **O-06** | **No registered `LG` file covers third-party intellectual property or content licensing.** The 24-file `LG` register was checked row by row during authoring: `LG-020` is Acceptable Use and Internal Access, `LG-024` is Regulatory Disclosure. This register therefore carries a licensing obligation with no legal artefact behind it. Raised as audit finding **KB-02** | Legal Counsel with Programme Content Lead | **W2 — `LB-01` classification has no policy to classify against** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Knowledge_Article.md` — all template sections retained in order, Reference-type interpretation stated in the headings, additions §11–§14 justified
- [x] Licence classification is a hard gate, with a usable honest default for the unconfirmed case
- [x] Register/file boundary stated — entries here, files in `M24` (`BRU-KMS-01`, `M61` T-04)
- [x] Redistribution scope propagates to citing articles (`LB-03`, `KA-09`)
- [x] Offline extract rule stated — extracts only, never full manuals
- [x] Coverage backlog ranking method stated, not asserted
- [x] Every factual and statutory claim carries a source and verification date
- [x] All internal links resolve
- [x] `BRU-KMS-*` cited to `M61` §9, not to `05-05`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Named approvers recorded — **pending Quality Manager and Legal Counsel**
- [ ] `O-02` brand-agreement documentation rights confirmed — **outstanding; the register cannot leave `restricted_pending_confirmation` at scale without it**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
