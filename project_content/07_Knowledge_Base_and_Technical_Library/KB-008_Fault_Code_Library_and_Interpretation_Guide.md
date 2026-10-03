---
id: KB-008
title: Fault Code Library and Interpretation Guide
project: 1000FiX ERP System v2.0
content_type: Knowledge article
template: TPL_Knowledge_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-16
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Technical
author: Technical Services with MDM and Specialist Technicians (R12)
reviewers: [Quality Manager, Technical Director, BI Lead, Knowledge Manager, Warranty Claims Officer, Localisation Lead]
approver: Technical Director
content_class: C
purpose: >
  Maps every manufacturer fault code, error code, beep code, blink pattern and alarm the company
  encounters onto the internal fault taxonomy in MD-024, with an interpretation and a next action.
  It is the bridge between what the device reports and what the company records; without it,
  diagnostic data cannot be aggregated, first-time-fix cannot be measured by cause, warranty claims
  cannot cite a code the brand recognises, and the AI triage model learns from a vocabulary that
  changes with every manufacturer.
traces_to: [MD-024, MD-021, MD-025, M31, M01, M26, M32, M61, M09, P02, P03, P08, KB-001, KB-002, KB-004, KB-005, KB-006, KB-007, KB-010, SP-033, RP-001]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: KB-008_Fault_Code_Library_and_Interpretation_Guide_BN.md
sources:
  - source: project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md — symptom and fault are distinct code types that must never share a code; FLT-01/02 hard rules; FLT-05 job-level creation flags for taxonomy review
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §5.1 FR-KMS-006 operational linkage; §9 BRU-KMS-12 governed AI corpus with citation
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/J_Data_Analytics_and_Intelligence/M26_AIML_Services_and_Model_Operations.md — BRU-AIM-01 human confirmation for material recommendations; BRU-AIM-02 guard rails
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-WTY-01 — a warranty claim requires a technician diagnosis; BRU-SRM-06 rework auto-flagging on same device and fault category within 30 days
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-004 first-time fix; KPI-013 automatic assignment rate; KPI-026 AI first-contact resolution
    verified: 2026-08-16
    class: P1
supersedes: none
review_due: 2027-02-16
---

# KB-008 — Fault Code Library and Interpretation Guide

| Item | Value |
|---|---|
| Article type | **Reference** |
| Device family | All — `DF-IT`, `DF-HA`, `DF-MB`, `DF-SRV`, `DF-SEC` |
| Brand / model scope | Every brand and model whose devices emit a code; scoped per mapping |
| Skill level required | L1 to read a mapping · L2/L3 to act on many outcomes · R12 or Technical analyst to create a mapping |
| Offline pack member | **Yes — high priority.** A code lookup is exactly what a technician needs with no signal |
| Review due | 2027-02-16 |

> **Template conformance.** Reference-type article; all `TPL_Knowledge_Article.md` sections
> retained in order and answered at library level. Sections 11–14 are justified additions.

---

## 1. Purpose and Scope

**The problem this library solves.** A device tells you something. A Samsung AC shows `E1`. A
different brand's AC also shows `E1` and means something else entirely. A desktop emits three
beeps. A UPS blinks a pattern. An NVR reports a numeric code. A phone shows a recovery screen. Each
manufacturer has its own vocabulary, none of them coordinate, and several reuse the same short
strings for unrelated conditions.

Meanwhile `MD-024` requires that **every service order carries a symptom code at intake and a
confirmed fault code before completion** (`FLT-01`, `FLT-02`), drawn from one internal taxonomy. The
gap between the manufacturer's vocabulary and the company's taxonomy has to be crossed on every
coded job, by 200–400 technicians, consistently.

**This file is that bridge.** It is not a copy of manufacturer documentation — that would be a
`LIB-` entry under [`KB-003_Repair_Manual_Index_and_Source_Register.md`](KB-003_Repair_Manual_Index_and_Source_Register.md)
and would carry that file's licensing constraints. It is a **mapping**: manufacturer code →
internal `FLT-` code → interpretation → next action → confidence.

**In scope:** the mapping record structure; the code-class taxonomy; confidence levels and their
evidence requirements; governing rules `FC-01`…`FC-16`; unmapped-code handling; the relationship to
warranty claims and to AI triage; worked mappings by device family; and the coverage measure.

**Out of scope:**

| Subject | Owned by |
|---|---|
| The internal fault taxonomy itself | [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md) — **`KA-02` and `FLT-05` prohibit minting codes here** |
| The repair procedure a code leads to | `KB-004`…`KB-007` |
| Manufacturer documentation as held content | [`KB-003_Repair_Manual_Index_and_Source_Register.md`](KB-003_Repair_Manual_Index_and_Source_Register.md) |
| Brand bulletins that redefine a code's meaning | [`KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md`](KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md) |
| Recurring defects that produce a code | [`KB-011_Known_Issue_and_Workaround_Register.md`](KB-011_Known_Issue_and_Workaround_Register.md) |
| Triage routing from a symptom | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md) |

> **Why `P1` and not `P2`.** Every other file in this category is `P2` or below except `KB-001`,
> `KB-010` and `KB-013`. This one is `P1` because three separate measured outcomes depend on it:
> first-time fix by cause (`KPI-004`), automatic assignment (`KPI-013`), and AI triage quality
> (`KPI-026`). All three read fault codes, and all three degrade to noise if the codes are applied
> inconsistently.

---

## 2. Safety

> ⚠ **WARNING — a code is not a diagnosis, and some codes are safety events.** Certain
> manufacturer codes indicate an active hazard rather than a component fault: refrigerant leak
> detection on an A2L/A3 system, battery over-temperature, earth-leakage trip, gas valve failure,
> overcurrent (hazard). Treating them as ordinary faults to be cleared and re-tested can cause
> fire, electric shock or refrigerant release (consequence). **Every mapping carries a `safety`
> flag; a mapping flagged `safety` routes to the safety procedure before any diagnostic step, and
> the code is never simply cleared** (avoidance). `MD-024` `FLT-04` already blocks routine closure
> on a safety-severity fault; this library is where the manufacturer's code is recognised as one.

> **NOTICE — clearing a code destroys evidence.** On many systems, clearing an error log removes
> the history a warranty claim, a known-issue investigation or a brand query would have relied on.
> **Capture the code, the log and the conditions before clearing** — `FC-11`.

---

## 3. Symptoms — *Reference article: what a coded fault looks like at the point of use*

| Code presentation | Where it appears | Family | Capture method |
|---|---|---|---|
| Alphanumeric on a display panel | AC, refrigerator, washing machine, oven | `DF-HA` | Photograph the panel |
| Blink or flash pattern on an LED | AC outdoor unit, UPS, camera, router | `DF-HA`, `DF-SRV`, `DF-SEC` | Video the pattern — **counts and gaps matter** |
| Audible beep code at power-on | Desktop, server | `DF-IT`, `DF-SRV` | Count and record the pattern; note the board vendor |
| Numeric or text error in firmware / BIOS | Desktop, laptop, server | `DF-IT`, `DF-SRV` | Screen photograph |
| Management-controller event log entry | Server, storage | `DF-SRV` | Log export |
| Recovery / DFU / bootloader state | Smartphone, tablet | `DF-MB` | Screen photograph |
| Application or OS error string | All | All | Screenshot |
| SMART attribute threshold | Storage | `DF-IT`, `DF-SRV` | Attribute export |
| Alarm text on an NVR or access controller | CCTV, access control | `DF-SEC` | Screenshot + log |
| Fault code printed on a service report by the device | Some appliances | `DF-HA` | Attach |

**`FC-01`: the code is captured as evidence, not transcribed from memory.** A photograph, a video
of a blink pattern, or a log export is attached to the job. A technician recalling "I think it said
E4" is how a mapping library acquires wrong data that then trains a model.

---

## 4. Likely Causes — *Reference article: why a mapping is wrong or missing*

| # | Cause | Frequency | Confirming test |
|---:|---|---|---|
| 1 | The code has never been encountered before | **Highest initially** | Query the library; no mapping returned |
| 2 | The same code string means different things on different brands or generations | **High and dangerous** | Compare mappings scoped to other brands |
| 3 | The manufacturer changed the meaning in a firmware revision | Medium | Check `KB-010` bulletins for that model |
| 4 | The mapping was created from a single observation and generalised too far | Medium | Check the mapping's confidence level and evidence count |
| 5 | The internal `FLT-` code the mapping points at has been retired or restructured | Low but silent | `MD-024` change log; `KA-15` re-tagging flag |
| 6 | The code is a symptom, not a fault, and was mapped to a `FLT-` code prematurely | Medium | `MD-024` distinguishes `SYM-` from `FLT-`; **they must never share a code** |
| 7 | The code indicates a condition outside the device — supply voltage, water pressure, network | Medium | Environment check |

> **Cause 6 is the conceptual error this library is most likely to make.** `MD-024` opens with the
> rule: *a symptom is what the customer reports before anyone looks; a fault is what the technician
> confirms.* A manufacturer code sits between them. `E1` on an AC is closer to a symptom — it tells
> you a sensor circuit is open, not why. **`FC-02`: a mapping may target a `SYM-` code, a `FLT-`
> code, or both, and must declare which.** Forcing every manufacturer code onto a `FLT-` code
> destroys exactly the distinction `MD-024` exists to protect.

---

## 5. Diagnostic Procedure — *how a technician uses this library*

| Step | Action | Expected | If not |
|---:|---|---|---|
| 1 | Capture the code as evidence (`FC-01`) | Photograph, video or log attached | Do not proceed on recall |
| 2 | Resolve the device to a `model_code` in `MD-021` | Single model | Register the model first (`MDL-01`) |
| 3 | Look up the code **scoped to that brand and model generation** | One mapping returned | Go to step 5 |
| 4 | Read the mapping: interpretation, `safety` flag, `SYM-`/`FLT-` target, next action, confidence | Understood | — |
| 5 | If no mapping: check brand and family-wide scopes, then `KB-010` bulletins | A candidate found | Go to step 7 |
| 6 | If the mapping is `low` confidence, treat it as a hypothesis, not an answer | Diagnosis continues | — |
| 7 | **Unmapped code:** record it as an unmapped observation against the model with the evidence, and continue diagnosing without it | Observation logged | — |
| 8 | On resolution, submit the confirmed relationship back to the library (§6.2) | Mapping proposed | — |

**`FC-03`: an unmapped code never blocks a repair.** The technician diagnoses without it and the
library learns from the outcome. A library that stops work when it does not know something will be
worked around, and a worked-around library stops receiving data.

---

## 6. Repair Procedure — *Reference article: how a mapping is created, verified and retired*

### 6.1 Mapping record structure

| Column | Type | Req | Constraint | Description |
|---|---|:--:|---|---|
| `mapping_code` | char(10) | ✔ | `FCM-nnnnn`, permanent | Never reused |
| `code_string` | text(40) | ✔ | As the device displays it, exactly | `E1`, `0x8007`, `3 short 1 long`, `blink 2-3` |
| `code_class` | enum | ✔ | display_code / blink_pattern / beep_code / firmware_error / log_event / recovery_state / smart_attribute / alarm_text | §3 |
| `brand_code` | fk | ✔ | → `MD-017` | **Scoping is mandatory — `FC-04`** |
| `model_scope` | multi-fk | ✔ | → `MD-021`, or `family_wide` within the brand | Never global |
| `generation_note` | text(120) |  |  | Firmware or generation qualifier |
| `device_family_code` | fk | ✔ | → `MD-021` §2.1 | |
| `target_type` | enum | ✔ | symptom / fault / both | **`FC-02`** |
| `sym_code` | fk |  | → `MD-024` `SYM-` | Required when `target_type` includes symptom |
| `flt_code` | fk |  | → `MD-024` `FLT-` | Required when `target_type` includes fault |
| `interpretation_en` | text(400) | ✔ |  | What the device is actually reporting |
| `interpretation_bn` | text(400) | ✔ |  | **Bengali is the field-reading language** |
| `next_action_en` | text(400) | ✔ |  | The first diagnostic step, not the repair |
| `next_action_bn` | text(400) | ✔ |  | |
| `safety_flag` | bool | ✔ |  | **`FC-05`** — routes to safety procedure first |
| `clears_evidence` | bool | ✔ |  | Whether clearing the code destroys the log (`FC-11`) |
| `article_ref` | fk |  | → `KNW-` | The repair guidance |
| `confidence` | enum | ✔ | manufacturer_documented / verified_observed / observed / **proposed** | §6.3 |
| `evidence_count` | int | ✔ |  | Number of confirmed observations behind it |
| `source_ref` | text(300) | ✔ |  | `LIB-` entry, `BUL-` bulletin, or observation set |
| `warranty_relevant` | bool | ✔ |  | Whether a brand claim may cite it (`BRU-WTY-01`) |
| `created_by` / `verified_by` | fk | ✔ |  | Author and verifier must differ (`FC-08`) |
| `status` | enum | ✔ | active / superseded / withdrawn | |

### 6.2 How a mapping is created

| Step | Who | Action | Gate |
|---:|---|---|---|
| 1 | Technician | Encounters a code; captures evidence; resolves the job | `FC-01` |
| 2 | Technician | Proposes the relationship: this code, on this model, was this confirmed fault | Enters at `confidence: proposed` |
| 3 | Technical analyst | Checks that the `SYM-`/`FLT-` target exists in `MD-024` | **Hard block — `KA-02`, `FC-06`: no code minted here** |
| 4 | Technical analyst | Checks brand and model scoping is not over-broad | `FC-04` |
| 5 | R12 or Technical analyst **other than the proposer** | Verifies against documentation (`LIB-`), a bulletin (`BUL-`), or further observations | `FC-08` |
| 6 | Technical analyst | Sets confidence per §6.3; sets `safety_flag` and `clears_evidence` | `FC-05`, `FC-11` |
| 7 | HSE Lead | Approves any mapping with `safety_flag: true` | `BRU-KMS-03` |
| 8 | System | Publishes; adds to offline packs; exposes to `M32` if confidence is sufficient | `FC-13` |
| 9 | Localisation | Bengali interpretation and next action, signed off in context | `BN-018` |

### 6.3 Confidence levels

**Confidence is the honesty mechanism of this library.** A mapping asserted with certainty from one
observation is worse than no mapping, because a technician will trust it.

| Level | Basis | Evidence required | May the AI cite it? | Shown to the technician as |
|---|---|---|:--:|---|
| `manufacturer_documented` | Stated in a held manual (`LIB-`) or brand bulletin (`BUL-`) | The document reference | ✔ | Authoritative |
| `verified_observed` | Confirmed by ≥ 5 independent jobs with consistent confirmed faults, verified by a second person | Job references | ✔ | Reliable |
| `observed` | 2–4 consistent observations | Job references | ✖ | **"Observed pattern — confirm before acting"** |
| `proposed` | 1 observation, unverified | Job reference | ✖ | **"Unverified — treat as a hypothesis"** |

**`FC-07`: confidence is displayed to the reader, always.** A technician who cannot see how much a
mapping is worth cannot calibrate how much to rely on it.

**`FC-13`: only `manufacturer_documented` and `verified_observed` mappings enter the `M32` corpus**
(`BRU-KMS-12`). An assistant that answers a customer from a single unverified observation is
producing confident fiction with a citation attached, which is worse than saying it does not know.

### 6.4 Governing rules

| # | Rule | Class |
|---|---|:--:|
| **FC-01** | The code is captured as evidence — photograph, video or log — not transcribed from recall | **H** |
| **FC-02** | Every mapping declares whether it targets a symptom, a fault, or both | **H** |
| **FC-03** | An unmapped code never blocks a repair | **H** |
| **FC-04** | Every mapping is scoped to a brand and a model or family; **no mapping is global** | **H** |
| **FC-05** | Safety-indicating codes carry `safety_flag: true` and route to the safety procedure before diagnosis | **H** |
| **FC-06** | No `SYM-` or `FLT-` code is created here; `MD-024` owns the taxonomy (`KA-02`, `RG-01`) | **H** |
| **FC-07** | Confidence is displayed to the reader on every mapping | **H** |
| **FC-08** | The verifier of a mapping is not its proposer (`BRU-KMS-02` pattern) | **H** |
| **FC-09** | A mapping whose `MD-024` target is retired is flagged for re-mapping, not silently repointed | **C** |
| **FC-10** | Where two brands use the same code string for different conditions, both mappings exist and neither is broadened | **H** |
| **FC-11** | Mappings whose codes destroy logs when cleared carry `clears_evidence: true` and instruct capture-before-clear | **H** |
| **FC-12** | A mapping contradicted by a brand bulletin is superseded on receipt of the bulletin, not at the next review | **C** |
| **FC-13** | Only `manufacturer_documented` and `verified_observed` mappings enter the `M32` corpus | **C** |
| **FC-14** | `warranty_relevant` mappings are checked against what the brand's claim process actually accepts before being flagged | **H** |
| **FC-15** | Bengali interpretation and next action are mandatory; this library is read in the field | **H** |
| **FC-16** | Coverage is measured as the proportion of **observed** codes that are mapped, not as an absolute count | **C** |

---

## 7. Parts — *Reference article: not applicable*

A mapping consumes no parts. Where a mapping's `next_action` leads to a part, the part is named in
the linked `KNW-` article under `AU-10`, never in the mapping itself — a mapping that names a part
becomes a repair instruction and escapes the review path that repair instructions require.

---

## 8. Verification and QC

| Test | Pass criterion | Recorded in |
|---|---|---|
| Every mapping targets an existing `MD-024` code | 100% (`FC-06`) | Weekly integrity report |
| Every mapping is brand- and model-scoped | 100% (`FC-04`) | Weekly |
| Confidence displayed on every mapping | 100% (`FC-07`) | Rendering check |
| Verifier ≠ proposer | 100% (`FC-08`) | Workflow record |
| `safety_flag` mappings have HSE approval | 100% (`BRU-KMS-03`) | Approval record |
| Bengali interpretation and next action present | 100% (`FC-15`) | Weekly |
| `M32` corpus contains no `observed` or `proposed` mappings | Zero (`FC-13`) | Corpus audit |
| Duplicate code strings across brands both mapped, neither broadened | Zero broadened (`FC-10`) | Monthly review |
| **Mapping accuracy** — proposed target vs confirmed bench fault | Rising; measured against jobs where both were recorded | Monthly |
| **Coverage** — observed codes with an active mapping | Rising; target set at first measurement (`FC-16`) | Weekly |
| Unmapped-code queue age | Nothing older than 30 days without triage | Weekly |

> **Mapping accuracy is the measure that matters** and it is computable for free: for every job
> that recorded both a manufacturer code and a confirmed `FLT-` code, does the mapping agree? A
> systematically wrong mapping shows up as a cluster, and a cluster is a fix.

---

## 9. Resolution Coding — *Reference article: the relationship, not a code of its own*

A mapping does not carry an `MD-025` resolution code. It carries a **`next_action`**, which is a
diagnostic step, not a repair outcome. The resolution is recorded on the job by the technician after
the repair, and the pairing of (manufacturer code → confirmed `FLT-` → recorded `RES-`) is what
makes the whole chain measurable:

| Chain element | Owned by | Recorded when |
|---|---|---|
| Manufacturer code observed | This library | At diagnosis |
| Confirmed `FLT-` code | `MD-024` | At diagnosis (`FLT-02` blocks completion without it) |
| `RES-` resolution and `standard_minutes` | `MD-025` | At completion (`RES-01` blocks completion without it) |
| Repair guidance used | `KNW-` article | At the point of use, with usefulness feedback |

**That four-element chain is the whole analytical value of this category.** It is what turns
"the AC showed E1" into "on this model, E1 means an open sensor circuit, it is fixed by replacing
the sensor, it takes N minutes, and the article that explains it resolved the fault 94% of the
time."

---

## 10. Escalation

| Escalate when | To | With what evidence |
|---|---|---|
| A code appears to indicate a safety condition and is not flagged | HSE Lead + Technical analyst — **flag it immediately** | Code, model, observed behaviour |
| A mapping is contradicted by a brand bulletin | Technical analyst; supersede on receipt (`FC-12`) | Bulletin reference |
| Two brands' mappings for one string are being confused in practice | Technical analyst + Knowledge Manager; review presentation, not just data | Job examples |
| A `warranty_relevant` mapping is rejected by the brand's claim process | Warranty Claims Officer (R28) + Technical analyst | Rejection record |
| An unmapped code appears repeatedly on a high-volume model | Technical analyst; prioritise the mapping | Occurrence count |
| A mapping's target `FLT-` code has been retired | MDM + Technical analyst (`FC-09`, `KA-15`) | Change log |
| `M32` is found citing an `observed` or `proposed` mapping | **CTO — corpus boundary breach** (`FC-13`, `BRU-KMS-12`) | Answer transcript |
| A manufacturer changes a code's meaning in firmware | Technical analyst; scope the existing mapping by generation | Firmware version evidence |

---

## 11. Worked Mappings *(addition — justified: the record structure alone does not show an author what "good" looks like; `KB-002` §4.11 uses the same device)*

**Illustrative shape only.** Real values must come from held documentation or verified observation.
**No mapping below is asserted as fact** — each shows the *form* a mapping takes, with the fields an
author must complete, and all are marked accordingly.

| Field | Example A | Example B | Example C |
|---|---|---|---|
| `mapping_code` | `FCM-00104` | `FCM-00871` | `FCM-01330` |
| `code_string` | `E1` *(as displayed)* | `3 short beeps` | `blink 2-3` *(outdoor LED)* |
| `code_class` | `display_code` | `beep_code` | `blink_pattern` |
| `brand_code` | One specific `BRD-` | One specific board vendor | One specific `BRD-` |
| `model_scope` | Named split-AC generation | Named desktop board family | Named AC outdoor family |
| `device_family_code` | `DF-HA` | `DF-IT` | `DF-HA` |
| `target_type` | `symptom` | `symptom` | `both` |
| `sym_code` | An `MD-024` sensor-circuit symptom | An `MD-024` POST-failure symptom | An `MD-024` outdoor-fault symptom |
| `flt_code` | — *(the fault is confirmed at the bench)* | — | An `MD-024` fault where documented |
| `interpretation_en` | "Indoor temperature sensor circuit open or out of range — the unit is reporting a sensor reading it cannot use" | "Power-on self-test halted at the memory stage on this board family" | "Outdoor unit reporting a protection trip" |
| `next_action_en` | "Measure sensor resistance against the model's temperature table before replacing anything" | "Reseat memory, then test single-module" | "**Do not reset repeatedly.** Identify why protection tripped" |
| `safety_flag` | `false` | `false` | **`true`** |
| `clears_evidence` | `true` — clearing removes the fault history | `false` | `true` |
| `confidence` | `manufacturer_documented`, cited to a `LIB-` entry | `manufacturer_documented`, cited to the board vendor's documentation | `verified_observed`, 7 jobs |
| `warranty_relevant` | `true` | `false` | `true` |

> **What example C demonstrates and every author should copy.** The `next_action` opens with what
> **not** to do. A protection trip that is repeatedly reset is a fault being converted into a
> failure, and the instruction that prevents it has to arrive before the instruction that
> diagnoses it.

---

## 12. Coverage, Backlog and the AI Relationship *(addition — justified: `FC-16` defines coverage and the measure needs its method stated)*

| Measure | Definition | Reported |
|---|---|---|
| **Observed-code coverage** | Distinct (brand, model-family, code string) combinations observed on jobs in the last 90 days that have an `active` mapping | Weekly |
| High-volume gap list | Unmapped combinations ranked by 90-day occurrence | Weekly — this is the authoring backlog |
| Confidence distribution | Share of mappings at each level; **the `proposed` share should fall over time** | Monthly |
| Mapping accuracy | Agreement between mapped target and confirmed bench fault | Monthly |
| Corpus eligibility | Share of mappings meeting `FC-13` | Monthly |
| Safety-flag review | All `safety_flag` mappings reviewed | Quarterly |

**The AI relationship, stated precisely.** `M26` triage and `M32` conversational answers both
benefit from this library, and both can be damaged by it:

| Benefit | Risk | Control |
|---|---|---|
| A code plus a model is the strongest single predictor available at triage | A wrong mapping trains the model on a wrong association | `FC-13` corpus boundary; mapping-accuracy measure |
| Codes give the AI a bounded vocabulary to reason over | The AI generalises a brand-scoped mapping to another brand | `FC-04`, `FC-10`; scoping is data, not prose |
| Citation is straightforward — a mapping has an ID and a version | A confident answer from a `proposed` mapping | `FC-07`, `FC-13`, `BRU-KMS-12` |
| Human confirmation stays in the loop | Automation drift | `BRU-AIM-01` — material recommendations require human confirmation; `BRU-AIM-02` guard rails |

---

## 13. Related Documents *(addition — justified: category convention)*

| Document | Relationship |
|---|---|
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md) | The taxonomy every mapping targets; names `KB-008` as a consumer |
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md) | Completes the four-element chain in §9 |
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md) | Model scoping under `FC-04` |
| [`KB-003_Repair_Manual_Index_and_Source_Register.md`](KB-003_Repair_Manual_Index_and_Source_Register.md) | `LIB-` sources for `manufacturer_documented` confidence |
| [`KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md`](KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md) | Bulletins that create or supersede mappings (`FC-12`) |
| [`KB-011_Known_Issue_and_Workaround_Register.md`](KB-011_Known_Issue_and_Workaround_Register.md) | A code recurring on one model is a known-issue signal |
| [`KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md`](KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md) · [`KB-005_Troubleshooting_Guide_Set_Home_Appliance.md`](KB-005_Troubleshooting_Guide_Set_Home_Appliance.md) · [`KB-006_Troubleshooting_Guide_Set_Mobile_and_Tablet.md`](KB-006_Troubleshooting_Guide_Set_Mobile_and_Tablet.md) · [`KB-007_Troubleshooting_Guide_Set_Server_Network_and_CCTV.md`](KB-007_Troubleshooting_Guide_Set_Server_Network_and_CCTV.md) | Every set links its coded-fault symptoms here |
| [`KB-016_Technician_Field_Reference_Card_Set.md`](KB-016_Technician_Field_Reference_Card_Set.md) | Code lookup is a top-priority offline card |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md) | Trees consume mappings at their nodes |
| `RP-001` KPI definitions | `KPI-004`, `KPI-013`, `KPI-026` all read fault codes |
| `M26` AI/ML Services · `M32` Conversational AI | Corpus consumers under `FC-13` |

---

## Sources and Currency

| Source | Verified | Next review |
|---|---|---|
| `MD-024` — symptom/fault distinction; `FLT-01`, `FLT-02`, `FLT-04`, `FLT-05`; `KB-008` named as a consumer in `MD-024` §5 and §11 | 2026-08-16 | 2027-02-16 |
| `MD-025` `RES-01`, `RES-02`; `MD-021` `MDL-01` | 2026-08-16 | 2027-02-16 |
| `M61` §5.1 FR-KMS-006; §9 `BRU-KMS-02`, `BRU-KMS-03`, `BRU-KMS-12` | 2026-08-16 | 2027-02-16 |
| `05-05` §2 `BRU-AIM-01`, `BRU-AIM-02`; `BRU-WTY-01`; `BRU-SRM-06` | 2026-08-16 | 2027-02-16 |
| `06-02` `KPI-004`, `KPI-013`, `KPI-026` | 2026-08-16 | 2027-02-16 |

> **No manufacturer code value in this file is asserted as fact.** §11 is explicitly labelled as
> illustrative form. Under `CG-012` a code interpretation is a factual claim about a third party's
> product and requires a `LIB-` or `BUL-` source at `manufacturer_documented` confidence, or a
> recorded observation set below it. Publishing a specific brand's code meaning here, unsourced,
> would put an unverifiable claim into 200–400 technicians' offline packs.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The library is empty.** This file is its specification. Population depends on `KB-003` holding manuals (blocked on `KB-003` `O-02` licensing) and on job volume generating observations | Technical analyst with Technical Library Owner | **Population starts W2; meaningful coverage by W4** |
| **O-02** | `MD-024` does not yet contain the `SYM-`/`FLT-` codes most mappings will target. **`FC-06` forbids minting them here**, so the taxonomy must be populated first | Technical analyst (MDM) | **W1–W2 — blocking** |
| **O-03** | The mapping-accuracy measure in §8 requires jobs to record both the manufacturer code and the confirmed fault. **Whether `M01`/`M31` capture the manufacturer code as a structured field is unconfirmed**; if it is free text, the measure is not computable | BI Lead with CTO | **Before W2 build — the measure depends on it** |
| **O-04** | `warranty_relevant` (`FC-14`) requires knowing what each brand's claim process accepts. That knowledge sits with R28 and with `MD-017`, and is not documented | Warranty Claims Officer with Commercial | W4 |
| **O-05** | The offline representation of a code lookup is not designed. A searchable mapping table is the single most-wanted offline artefact and it is not the same shape as an article | Content Design with `P02` team | W2 |
| **O-06** | Bengali interpretation wording (`FC-15`) for technical code meanings requires the terminology base that `KB-002` `O-05` records as missing | Localisation Lead with R12 | W2 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Knowledge_Article.md`; additions §11–§13 justified
- [x] The symptom-versus-fault distinction from `MD-024` preserved rather than collapsed (`FC-02`)
- [x] Code minting prohibited; `MD-024` named as the owning register (`FC-06`, `KA-02`)
- [x] Brand and model scoping mandatory; global mappings prohibited (`FC-04`, `FC-10`)
- [x] Confidence levels defined with evidence requirements and displayed to the reader
- [x] AI corpus boundary bound to confidence (`FC-13`, `BRU-KMS-12`)
- [x] Safety-indicating codes flagged and routed before diagnosis
- [x] Capture-before-clear rule stated (`FC-11`)
- [x] Unmapped codes never block a repair (`FC-03`)
- [x] Worked mappings shown as **form only**, with no unsourced brand claim asserted
- [x] Coverage defined against observed codes, not as an absolute
- [x] All internal links resolve
- [x] `BRU-KMS-*` cited to `M61` §9; `BRU-AIM-*`, `BRU-WTY-*`, `BRU-SRM-*` cited to `05-05`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-02` `MD-024` populated — outstanding; blocking**
- [ ] **`O-03` manufacturer code captured as a structured field — outstanding; the accuracy measure depends on it**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approver recorded — **pending Technical Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
