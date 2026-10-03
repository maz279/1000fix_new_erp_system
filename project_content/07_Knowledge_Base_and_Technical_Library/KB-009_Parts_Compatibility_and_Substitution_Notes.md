---
id: KB-009
title: Parts Compatibility and Substitution Notes
project: 1000FiX ERP System v2.0
content_type: Knowledge article
template: TPL_Knowledge_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-16
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Technical with Inventory
author: Technical Services with Inventory and Specialist Technicians (R12)
reviewers: [Quality Manager, Technical Director, Inventory Manager, Warranty Claims Officer, HSE Lead, Knowledge Manager, Localisation Lead]
approver: Technical Director with Inventory Manager
content_class: C
purpose: >
  The technical knowledge layer over the parts master — cross-references, approved substitutes,
  prohibited substitutions, quality tiers and the behavioural consequences of fitting a non-genuine
  part. Wrong-part fitting is a leading cause of rework and of brand-warranty claim rejection, and
  neither the compatibility matrix in MD-022 nor a technician's memory can carry the judgement
  about when a technically compatible part is nevertheless the wrong answer.
traces_to: [MD-022, MD-021, MD-031, M15, M43, M09, M31, M61, P02, P03, P08, KB-001, KB-002, KB-004, KB-005, KB-006, KB-007, KB-013, SP-016]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: KB-009_Parts_Compatibility_and_Substitution_Notes_BN.md
sources:
  - source: project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md — part_class enum (oem / oem_equivalent / compatible / refurbished) affects warranty and claim eligibility; supersedes_part_code and substitutes columns; hazard_class enum
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-WTY-01 claim evidence requirements including the replaced-parts list; BRU-WTY-04 brand-supplied warranty parts cannot be consumed on non-warranty jobs; BRU-INV-05 expired shelf-life stock cannot be issued; BRU-INV-07 goods failing inspection go to quarantine; BRU-INV-08 serialised parts captured at receipt and issue
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §5.4 FR-KMS-028 — draft articles created from recurring M09 claim-rejection causes
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M09_Warranty_Protection_Plans_and_Claims.md — claim rejection causes and reimbursement cycle
    verified: 2026-08-16
    class: P1
supersedes: none
review_due: 2027-02-16
---

# KB-009 — Parts Compatibility and Substitution Notes

| Item | Value |
|---|---|
| Article type | **Reference** |
| Device family | All |
| Brand / model scope | Scoped per note |
| Skill level required | L1 to read · L2/R12 to author · Technical Director + Inventory Manager to approve a prohibition |
| Offline pack member | **Yes** — substitution decisions are made at the bench and in the van, not at a desk |
| Review due | 2027-02-16 |

> **Template conformance.** Reference-type article; all `TPL_Knowledge_Article.md` sections
> retained in order and answered at register level. Sections 11–13 are justified additions.

---

## 1. Purpose and Scope

**`MD-022` answers "will it fit?". This file answers "should it go in?".**

The parts master already holds `compatible_models`, `substitutes`, `supersedes_part_code` and
`part_class`. Those are structural facts. What it cannot hold is the judgement layer:

| The question `MD-022` cannot answer | Where the answer lives |
|---|---|
| This part fits — but will the device behave differently? | §6.2 behavioural notes |
| This substitute is listed — but is it acceptable on **this** repair, for **this** customer, under **this** warranty? | §6.3 decision rules |
| This substitution is technically possible — is it **prohibited**? | §6.4 prohibited list |
| Two parts supersede each other in a chain — which end do I fit, and does the old one still work? | §6.5 supersession |
| The brand rejected our claim citing the part — why, and how do we stop it recurring? | §6.6 claim-rejection loop |

**In scope:** cross-reference and equivalence notes; quality tiers and what each costs the
customer and the company; the substitution decision rules; the prohibited-substitution register;
supersession chain handling; the claim-rejection feedback loop; and non-genuine part behavioural
effects.

**Out of scope:**

| Subject | Owned by |
|---|---|
| The part master, compatibility matrix and hazard classes | [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md) |
| Parts issue, return, van stock and reconciliation | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md) · `M15` |
| Procurement, sourcing and vendor quality | `M16`, `M42` |
| Warranty coverage terms | `MD-031` · `M09` |
| Hazard handling data | [`KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](KB-013_ESD_Chemical_and_Battery_Safety_Data.md) |
| Pricing of parts | `MD-029` |
| Demand planning from substitution patterns | `M43` — this file supplies the substitution facts, not the forecast |

---

## 2. Safety

> ⛔ **DANGER — safety-critical components must never be substituted below specification.** Fuses,
> thermal cut-outs, thermal fuses, door interlocks, earth conductors, pressure-relief devices,
> insulation-rated components and mains-rated capacitors exist to fail safely (hazard).
> Substituting a higher-rated fuse, a bypassed cut-out, a lower-voltage capacitor or an
> unrated interlock removes a protection the manufacturer put there and can cause fire,
> electrocution or explosion (consequence). **These components are on the prohibited-substitution
> register in §6.4 and are fitted only to the manufacturer's exact specification** (avoidance).

> ⚠ **WARNING — battery substitution.** Fitting a battery of the wrong chemistry, capacity,
> protection-circuit type or physical fit creates a thermal-runaway risk in a device the customer
> keeps beside them (hazard). Fire and injury (consequence). **Batteries are substituted only
> within the manufacturer's stated specification, with a protection circuit present, and never
> from an unverified source** (avoidance). Data in `KB-013` §4.

> ⚠ **WARNING — refrigerant-circuit components.** A component rated for one refrigerant class may
> not be safe on another. The A1 → A2L/A3 transition (`KB-005` §2) means an older-stock component
> may be unsuitable for a converted system (hazard). Leak, ignition (consequence). **Match the
> component to the system's actual refrigerant, not to the model's original one** (avoidance).

> **NOTICE — a technically working repair can still be the wrong one.** A `compatible`-class part
> that functions correctly can still void the customer's manufacturer warranty, cause a brand claim
> to be rejected, or disable a device feature. That is a commercial and reputational harm, and it is
> why §6.3 requires a decision, not a default.

---

## 3. Symptoms — *Reference article: the signals that substitution knowledge is failing*

| Signal | What it indicates | Where observed |
|---|---|---|
| Rework within 30 days on a job where a part was replaced | Wrong or poor-quality part fitted | `BRU-SRM-06` rework flag |
| Brand claim rejected citing the part | Wrong `part_class`, or a substitution the brand does not accept | `M09` rejection reasons |
| The same part is issued and returned repeatedly | Compatibility data is wrong | `SP-016` return reasons |
| A technician asks a colleague "will this one work?" | The note that should answer it does not exist | Escalation and chat volume |
| A device works but a feature is disabled after repair | Non-genuine part behavioural effect, undocumented | Customer complaint |
| Two part codes are used interchangeably in practice but not linked in `MD-022` | Missing substitution record | Consumption analysis |
| A part is fitted that is not on the compatibility matrix at all | Either the matrix is incomplete or the fit was wrong | Job vs `MD-022` reconciliation |

---

## 4. Likely Causes

| # | Cause | Frequency | Confirming test |
|---:|---|---|---|
| 1 | Compatibility matrix incomplete for a newer or grey-market model | **Highest** | `MD-022` `compatible_models` empty or thin |
| 2 | Substitute listed structurally with no note on its consequences | High | `substitutes` populated, no `KB-009` note |
| 3 | `part_class` not checked before fitting | High | Job record vs `part_class` |
| 4 | Supersession chain followed in the wrong direction | Medium | Fitted code vs `supersedes_part_code` |
| 5 | Non-genuine part sourced under time pressure during a stock-out | **Medium and rising in peak season** | Stock-out record vs fitted `part_class` |
| 6 | Brand changed its claim acceptance criteria without a bulletin reaching the bench | Medium | `M09` rejection cluster with no `BUL-` record |
| 7 | Refurbished part fitted without customer disclosure | Medium | Disclosure record absent |

---

## 5. Diagnostic Procedure — *the substitution decision, as a sequence*

**`PC-01`: this sequence runs before any part that is not the exact OEM part is fitted.**

| Step | Question | If yes | If no |
|---:|---|---|---|
| 1 | Is the exact OEM part available within the customer's agreed timeline? | Fit it. Sequence ends | Continue |
| 2 | **Is the component on the prohibited-substitution register (§6.4)?** | **Stop.** No substitution. Order the correct part or escalate | Continue |
| 3 | Is this a **brand warranty** job? | **Only brand-supplied or brand-approved parts.** `BRU-WTY-04` also blocks consuming brand consignment stock on non-warranty work | Continue |
| 4 | Is the device under **manufacturer warranty** (`MD-031`)? | A non-OEM part may void it. **Customer must decide, in writing** | Continue |
| 5 | Is the device under a **1000FiX contract or protection plan**? | Check the contract's parts standard before substituting | Continue |
| 6 | Is a substitute recorded in `MD-022` **and** does it carry a `KB-009` note? | Read the note; apply its conditions | **Do not improvise.** Propose a note (§6.7) and escalate |
| 7 | Does the substitute change device behaviour (§6.2)? | Tell the customer before fitting. Record it | Continue |
| 8 | Is the substitute `refurbished`? | **Disclose to the customer and record the disclosure**; state the warranty that applies to it | Continue |
| 9 | Fit, record the exact `part_code` and `part_class` on the job, capture serials where serialised | — | — |

> **Step 4 is the one most often skipped and the most expensive when it is.** A technically sound
> `compatible`-class repair on a device still under manufacturer warranty can transfer the whole
> future liability for that device from the manufacturer to 1000FiX and to the customer. It costs
> one question and one recorded answer.

---

## 6. Repair Procedure — *Reference article: how substitution knowledge is structured*

### 6.1 Quality tiers

`MD-022` defines `part_class` as an enum. This file states what each tier means in practice.

| `part_class` | What it is | Warranty on the device | Brand claim eligible | Customer disclosure | Typical use |
|---|---|---|---|:--:|---|
| `oem` | The manufacturer's own part | Preserved | ✔ | Not required | Warranty work, contracts, premium |
| `oem_equivalent` | Made to the OEM specification by a qualified supplier, verified by us | Usually preserved — **check per brand** | Usually ✖ | Recommended | Out-of-warranty standard repair |
| `compatible` | Fits and functions; not made to the OEM specification | **May be voided** | ✖ | **Required** | Cost-sensitive out-of-warranty, obsolete parts |
| `refurbished` | Recovered and reconditioned | Not applicable to the part's origin | ✖ | **Required, with the part's own warranty stated** | Obsolete parts, BER alternatives, trade-in stock |

**`PC-02`: `part_class` is recorded on every job line.** Not the part name — the class. A parts
list that says "battery" tells a claims officer nothing; one that says `oem` or `compatible` tells
them whether the claim will survive.

### 6.2 Behavioural notes — the non-genuine effect

A part can fit, function, and still change what the device does. This is most pronounced in
`DF-MB` and increasingly present in `DF-HA` and `DF-IT`.

| Effect class | Typical manifestation | Consequence for the customer |
|---|---|---|
| **Feature disabled** | A display-bound sensor, biometric, or automatic function stops working | The repair is "successful" and the customer has lost something |
| **Persistent warning** | The device shows a non-genuine-part message | The customer believes the repair failed |
| **Calibration required** | The part works only after a pairing or calibration step | Skipping it produces intermittent behaviour |
| **Reduced specification** | Lower capacity, lower brightness, lower thermal headroom | Slower degradation into a complaint |
| **Update behaviour** | A firmware update disables or degrades the part later | **The complaint arrives weeks after the repair, and looks like our fault** |
| **Safety-function difference** | A protection circuit behaves differently | Goes to §6.4 |

**`PC-03`: every recorded substitute carries a behavioural note, or an explicit statement that no
effect is known and the basis for that statement.** "No known effect, based on 12 fitted units over
6 months" is a useful note. Silence is not.

**`PC-04`: any effect that will be visible to the customer is disclosed before fitting**, not
explained afterwards.

### 6.3 Substitution decision rules

| # | Rule | Class |
|---|---|:--:|
| **PC-01** | The §5 sequence runs before any non-OEM part is fitted | **H** |
| **PC-02** | `part_class` is recorded on every job line | **H** |
| **PC-03** | Every recorded substitute carries a behavioural note or a sourced statement of no known effect | **H** |
| **PC-04** | Customer-visible effects are disclosed before fitting | **H** |
| **PC-05** | Brand warranty work uses brand-supplied or brand-approved parts only; brand consignment is never consumed on non-warranty work (`BRU-WTY-04`) | **H** |
| **PC-06** | Prohibited substitutions (§6.4) are never made, under any time pressure, by any level | **H** |
| **PC-07** | Refurbished parts are disclosed with their own warranty term stated | **H** |
| **PC-08** | Expired shelf-life stock is never issued (`BRU-INV-05`); parts failing inspection go to quarantine, never to available stock (`BRU-INV-07`) | **H** |
| **PC-09** | Serialised parts have serials captured at receipt and issue (`BRU-INV-08`) | **H** |
| **PC-10** | A substitution made under stock-out pressure is **recorded as such**, so the pattern is visible to planning (`M43`) | **C** |
| **PC-11** | A note may not create a `MD-022` record; compatibility and substitution data are registered there first (`KA-02`) | **H** |
| **PC-12** | A claim rejected on a part triggers the §6.6 loop within the reporting period, not at the next review | **C** |
| **PC-13** | Notes are scoped to brand and model family; no note is global | **H** |
| **PC-14** | Where a substitute is acceptable for a repair but **not** for a claim, the note says both plainly | **H** |

### 6.4 The prohibited-substitution register

**Substitution of these components is prohibited outright.** They are fitted to the manufacturer's
exact specification or not at all. The list is a **safety and liability control**, approved by the
Technical Director with the Inventory Manager and HSE Lead, and it is short by design — a long
prohibition list gets ignored.

| # | Component class | Family | Why prohibited |
|---:|---|---|---|
| 1 | Fuses and thermal fuses | All | A higher rating removes the protection; a lower one causes nuisance failure that invites bypassing |
| 2 | Thermal cut-outs and over-temperature protection | `DF-HA`, `DF-IT` | The device's last defence against fire |
| 3 | Door interlocks and safety switches | Microwave, laundry, access control | Radiation, mechanical and egress protection |
| 4 | Earth conductors, bonding straps and insulation-rated barriers | All mains devices | Shock protection |
| 5 | Mains-rated (X/Y class) capacitors | All mains devices | Failure mode is designed; a general capacitor fails short |
| 6 | Pressure-relief devices and refrigerant-circuit safety components | `DF-HA` | Explosion risk; class-specific |
| 7 | Battery protection circuits and battery packs from unverified sources | All | Thermal runaway |
| 8 | Brand-authorised security or attestation components | `DF-MB`, `DF-SRV` | Functional and legal consequences beyond the repair |
| 9 | Fire-alarm interface components in access control | `DF-SEC` | Life safety; outside our competence to substitute |

**`PC-15`: an addition to this register requires Technical Director, Inventory Manager and HSE Lead
approval; a removal requires the same three plus a recorded justification.** A prohibition is easy
to add under the pressure of a single incident and hard to remove afterwards, so both directions
carry the same gate.

### 6.5 Supersession chains

`MD-022` carries `supersedes_part_code` as a self-reference. In practice a chain forms:
`PRT-A` → `PRT-B` → `PRT-C`.

| Rule | Detail |
|---|---|
| **Fit the newest** | Unless a note says otherwise, the current end of the chain is what is fitted |
| **Backward compatibility is not symmetric** | A newer part usually replaces an older one; the reverse is often false. Notes must say which direction holds |
| **Chain notes are attached to the chain, not to one member** | So that a technician holding any member sees the whole picture |
| **Old stock is not obsolete stock** | An older chain member in stock may be perfectly correct for an older model. `PC-16`: a note states which models require the older member |
| **A superseded part may change form factor, connector or firmware requirement** | The note states what else must change with it |

### 6.6 The claim-rejection feedback loop

`M61` FR-KMS-028 requires draft articles to be created from recurring `M09` claim-rejection causes.
This is where parts-related rejections land.

| Step | Who | Action |
|---:|---|---|
| 1 | `M09` | A claim is rejected with a part-related reason |
| 2 | System | The rejection is grouped by (brand, model family, part, reason) |
| 3 | R28 Warranty Claims Officer | Confirms the reason is genuinely about the part, not about evidence or timing |
| 4 | Technical analyst | Creates or amends the `KB-009` note under `PC-14`: acceptable for repair, not acceptable for claim — or not acceptable at all |
| 5 | System | The note reaches the bench and the van via the offline pack |
| 6 | R28 | The rejection rate for that cause is tracked; if it does not fall, the note is not reaching the point of decision |

> **Step 6 is the honest test of this whole file.** A note that exists and does not change the
> rejection rate has not failed to be written — it has failed to be *found*, which is a `KB-001`
> tagging problem or a `KB-016` offline-card problem, not an authoring one.

### 6.7 Proposing a note

Any technician may propose a note from the bench under the `KB-002` Path A capture (three minutes,
Bengali, photographs). It enters the improvement queue, is verified by someone other than the
proposer, is checked against `MD-022` for structural truth, and is published with its evidence
count visible — the same confidence discipline `KB-008` §6.3 applies to code mappings.

---

## 7. Parts

This section is the file's subject; the structure is in §6. What belongs here is the **record**:

| Note field | Bound to | Note |
|---|---|---|
| `note_code` | `PCN-nnnnn`, permanent | Never reused |
| `part_code` / `substitute_part_code` | → `MD-022` | **Both must exist; `PC-11` forbids creating them here** |
| `brand_code`, `model_scope` | → `MD-017`, `MD-021` | `PC-13` — never global |
| `direction` | one-way / bidirectional | Supersession asymmetry (§6.5) |
| `acceptable_for_repair` | bool | |
| `acceptable_for_brand_claim` | bool | `PC-14` |
| `voids_manufacturer_warranty` | enum: yes / no / unknown | **`unknown` is a permitted and honest value** |
| `behavioural_effect` | text | `PC-03` |
| `customer_disclosure_required` | bool | `PC-04` |
| `hazard_note` | → `KB-013` section | Where `hazard_class` ≠ `none` |
| `evidence_count`, `confidence` | as `KB-008` §6.3 | |
| `source_ref` | `LIB-`, `BUL-`, or observation set | `CG-012` |
| `status` | active / superseded / withdrawn | |

---

## 8. Verification and QC

| Test | Pass criterion | Recorded in |
|---|---|---|
| Every note's part codes exist in `MD-022` | 100% (`PC-11`) | Weekly integrity report |
| Every note is brand- and model-scoped | 100% (`PC-13`) | Weekly |
| Every substitute carries a behavioural note or a sourced no-effect statement | 100% (`PC-03`) | Weekly |
| `part_class` recorded on every job line | 100% (`PC-02`) | Job audit |
| Prohibited-substitution register additions carry all three approvals | 100% (`PC-15`) | Approval record |
| Refurbished-part disclosures recorded | 100% (`PC-07`) | Job audit |
| Serialised parts captured at receipt and issue | 100% (`BRU-INV-08`) | Inventory audit |
| **Rework rate on jobs where a substitute was fitted** vs jobs with OEM | Substitute rework rate not materially higher; investigated where it is | Monthly |
| **Claim-rejection rate attributable to parts** | Falling (`PC-12`, §6.6) | Monthly to R28 |
| Stock-out-driven substitutions | Recorded and trending; feeds `M43` | Monthly |
| Notes reaching the bench — offline pack currency | > 98% current | Pack telemetry |

---

## 9. Resolution Coding

A substitution note carries no `MD-025` code of its own. It affects coding in three ways:

| Effect | Detail |
|---|---|
| `replace_part` resolutions record the exact `part_code` **and** `part_class` | `PC-02`; `RES-02` blocks completion without a part issue |
| `warranty_claimable` on the `RES-` code is not sufficient on its own | The **part** must also be claim-acceptable (`PC-14`). A claimable resolution with a non-claimable part is a rejection waiting to happen |
| Rework classification | A rework caused by a substitution is coded as rework (`BRU-SRM-06`) and attributed to the part, not to the technician, unless the §5 sequence was skipped |

---

## 10. Escalation

| Escalate when | To | With what evidence |
|---|---|---|
| A prohibited substitution is proposed or has been made | **Technical Director + HSE Lead immediately**; device withdrawn from the customer if already fitted | Job, part codes, photographs |
| No note exists and a substitution is needed under time pressure | Workshop Supervisor (R09) or Inventory Manager; **do not improvise** (`PC-01` step 6) | Part codes, timeline |
| A brand rejects claims repeatedly citing parts | R28 + Technical analyst; §6.6 loop | Rejection cluster |
| A substitute causes rework | Quality Manager; note amended or withdrawn | Rework records |
| Compatibility data in `MD-022` is found wrong | MDM + Inventory Manager | Evidence of the mismatch |
| A part fails inspection or is out of shelf life | Quarantine (`BRU-INV-07`, `BRU-INV-05`); Inventory Manager | Inspection record |
| A stock-out is driving repeated substitution on a high-volume part | Inventory Manager + `M43` planning | Stock-out and substitution counts |
| A customer disputes a disclosed substitution after the fact | Branch manager; the disclosure record settles it — **which is why `PC-04` requires it in advance** | Disclosure record |

---

## 11. Coverage and Backlog *(addition — justified: the note register needs a measurable target like every other `KB` register)*

| Measure | Definition | Target |
|---|---|---|
| **Substitute coverage** | Proportion of `MD-022` `substitutes` entries carrying a `KB-009` note | Rising; **100% for parts with `hazard_class` ≠ `none`** |
| High-consumption gap list | Parts in the top 200 by consumption with a listed substitute and no note, ranked by volume | Weekly backlog |
| Prohibited-register completeness | The nine classes in §6.4 mapped to actual `MD-022` records | 100% before W2 |
| Behavioural-note coverage for `DF-MB` | The family where non-genuine effects are strongest | 100% of display and battery substitutes before W4 |
| Note confidence distribution | `proposed` share falling over time | Monthly |

---

## 12. Related Documents *(addition — justified: category convention)*

| Document | Relationship |
|---|---|
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md) | The structural layer this file interprets; names `KB-009` as a consumer |
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md) | Model scoping under `PC-13` |
| [`KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](KB-013_ESD_Chemical_and_Battery_Safety_Data.md) | Hazard data for battery, refrigerant and chemical parts |
| [`KB-011_Known_Issue_and_Workaround_Register.md`](KB-011_Known_Issue_and_Workaround_Register.md) | A substitute that consistently fails is a known issue |
| [`KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md`](KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md) | Bulletins change part acceptability and supersession |
| [`KB-006_Troubleshooting_Guide_Set_Mobile_and_Tablet.md`](KB-006_Troubleshooting_Guide_Set_Mobile_and_Tablet.md) | `TG-31` non-genuine part effects — the strongest case in the library |
| [`KB-005_Troubleshooting_Guide_Set_Home_Appliance.md`](KB-005_Troubleshooting_Guide_Set_Home_Appliance.md) | Refrigerant-class component matching |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md) | The process that issues what this file governs |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md) | The claim process the §6.6 loop feeds |
| `MD-031` Warranty Type and Coverage Term Catalogue | The warranty status checked at §5 step 4 |
| `TR-012` Course Pack — Inventory and Store Keeper · `TR-009` Field Technician | Train the decision sequence |

---

## Sources and Currency

| Source | Verified | Next review |
|---|---|---|
| `MD-022` — `part_class` enum and its stated effect on warranty and claim eligibility; `substitutes`, `supersedes_part_code`, `hazard_class`; `KB-009` named as a consumer | 2026-08-16 | 2027-02-16 |
| `05-05` §2 `BRU-WTY-01`, `BRU-WTY-04`; `BRU-INV-05`, `BRU-INV-07`, `BRU-INV-08`; `BRU-SRM-06` | 2026-08-16 | 2027-02-16 |
| `M61` §5.4 FR-KMS-028 — draft articles from recurring claim-rejection causes | 2026-08-16 | 2027-02-16 |
| `M09` Warranty, Protection Plans and Claims — rejection causes | 2026-08-16 | 2027-02-16 |

> **No specific part number, brand equivalence or voiding claim is asserted in this file.** Every
> such statement is a factual claim about a third party's product and requires a `LIB-` or `BUL-`
> source, or a recorded observation set with a stated count (`CG-012`, `PC-03`). The prohibited
> classes in §6.4 are stated as **component classes**, not as part numbers, for the same reason.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The note register is empty.** `MD-022` must be populated first; notes then follow consumption. The §11 backlog cannot be computed until both exist | Technical analyst with Inventory | **Prohibited register (§6.4) mapped to real `MD-022` records before W2** |
| **O-02** | **`voids_manufacturer_warranty` cannot be answered for most brands** without the documentation `KB-003` `O-02` is blocked on. `unknown` is permitted, but a register that is mostly `unknown` does not support §5 step 4 | Warranty Claims Officer with Commercial and Legal | W4 |
| **O-03** | Whether `M15`/`M31` capture **stock-out-driven substitution** as a structured flag is unconfirmed. `PC-10` and the §8 measure depend on it | Inventory Manager with CTO | Before W2 build |
| **O-04** | The customer-disclosure wording for `compatible` and `refurbished` parts (`PC-04`, `PC-07`) has contractual consequence and does not exist. It belongs in a `DT` or `LG` artefact, not invented per job | Legal Counsel with Content Design | **W2 — `PC-04` is unusable without it** |
| **O-05** | Non-genuine behavioural effects for `DF-MB` (§6.2) require per-model-family data gathered from real repairs. Same gap as `KB-006` `O-05` | Technical Director with Inventory | W4 |
| **O-06** | The offline representation of a substitution decision is not designed — it is a decision tree, not an article. Same class of gap as `KB-008` `O-05` | Content Design with `P02` team | W2 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Knowledge_Article.md`; additions §11–§12 justified
- [x] The `MD-022`/`KB-009` boundary stated as structure versus judgement
- [x] Safety-critical components placed on an explicit prohibited-substitution register with a dual-direction approval gate
- [x] `part_class` consequences stated for warranty, claim and disclosure
- [x] Behavioural effects of non-genuine parts treated as required content, with "no known effect" permitted only when sourced
- [x] The substitution decision written as an ordered sequence usable at the bench
- [x] Supersession asymmetry stated
- [x] Claim-rejection feedback loop closed with a measure that tests whether the note was *found*
- [x] `unknown` permitted as an honest value for warranty voiding
- [x] All internal links resolve
- [x] `BRU-KMS-*` cited to `M61` §9; `BRU-WTY-*`, `BRU-INV-*`, `BRU-SRM-*` cited to `05-05`
- [x] No unsourced part-specific or brand-specific claim asserted
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` prohibited register mapped to real `MD-022` records — outstanding**
- [ ] **`O-04` customer-disclosure wording authored — outstanding; blocks `PC-04`**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Technical Director and Inventory Manager**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
