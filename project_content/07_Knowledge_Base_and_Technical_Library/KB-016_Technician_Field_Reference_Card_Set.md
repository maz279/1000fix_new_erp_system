---
id: KB-016
title: Technician Field Reference Card Set
project: 1000FiX ERP System v2.0
content_type: Knowledge article
template: TPL_Knowledge_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-16
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Technical with Content Design
author: Content Design with Technical Services and the P02 product team
reviewers: [Quality Manager, Technical Director, HSE Lead, Knowledge Manager, Localisation Lead, CTO, Learning and Development]
approver: Technical Director with Content Design Lead
content_class: D
purpose: >
  The curated set of one-screen reference cards shipped inside the technician application for
  offline use — safety, escalation, codes and the most-repeated procedures. P02 requires offline
  repair manuals and past repair notes; the offline pack must be curated rather than being the whole
  library, because a library that does not fit on the device is not offline at all, and a technician
  standing on a rooftop with no signal needs one screen, not a search result.
traces_to: [M61, M32, P02, P09, P11, MD-021, MD-024, MD-025, MD-011, KB-001, KB-002, KB-004, KB-005, KB-006, KB-007, KB-008, KB-009, KB-010, KB-011, KB-012, KB-013, KB-015, SP-030, SP-033, UI-012, VB-009, CG-011]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: KB-016_Technician_Field_Reference_Card_Set_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P02 non-negotiable requirements include full offline operation for 24 hours and offline access to repair manuals, wiring diagrams and past repair notes; complete Bengali UI including error messages
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §5.2 FR-KMS-017 scoped current offline article set within a declared storage budget, FR-KMS-018 incremental sync never leaving a stale article presented as current; §6 T-01 offline set scoping, T-02 media budget discipline, T-03 staleness visible offline, T-15 article open under 100 ms offline
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §9 BRU-KMS-05 superseded or retired articles removed from offline sets; §15 KPI-C61-07 technicians with a current offline set over 98%, KPI-C61-08 stale articles served offline zero
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §4 design position — offline is the primary mode not a degraded one; diagrams are the largest payload and the most valuable content, so the sync strategy is a genuine engineering problem
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §18 Q-04 — the offline storage budget per technician device is an open question, given that diagrams dominate the payload and P02 targets a mid-range Android with 3 GB RAM
    verified: 2026-08-16
    class: P1
supersedes: none
review_due: 2027-02-16
---

# KB-016 — Technician Field Reference Card Set

| Item | Value |
|---|---|
| Article type | **Reference** (`reference_card` article type) |
| Device family | All — the set spans every family a technician is scoped to |
| Brand / model scope | Universal cards plus family-scoped cards; **never model-specific** (§6.2) |
| Skill level required | **L1 — the set is designed for the least experienced person who will hold it** |
| Offline pack member | **This file defines the offline pack** |
| Review due | 2027-02-16 · individual cards on a **6-month cycle** (`KB-015` §4.3) |

> **Template conformance.** Reference-type article; all `TPL_Knowledge_Article.md` sections
> retained in order and answered at set level. Sections 11–13 are justified additions, consistent
> with [`KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md`](KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md) §11.

---

## 1. Purpose and Scope

**`M61` §4 states the design position: offline is the primary mode, not a degraded one.** This file
is where that position becomes a concrete deliverable.

### 1.1 Why a curated set rather than "the library, cached"

| Constraint | Consequence |
|---|---|
| **Storage budget on a mid-range Android** | `M61` Q-04 records the budget as undecided and notes that diagrams dominate the payload. Whatever the number, it will not hold everything |
| **Reading conditions** | One hand, outdoors, in sunlight, on a rooftop, in a customer's kitchen, in a crowded workshop, often standing |
| **Time available** | Seconds, not minutes. A technician consulting a reference has already stopped work |
| **Language** | Bengali-first (`P02` non-negotiable) with technical terms that mostly exist only in English |
| **Trust** | Abbreviated content removes the context that would let a reader spot an error, so cards must be **more** correct than articles, not less |

**A cached library fails all five.** A card set designed against them succeeds — but only if
something decides what is on it, and that is what this file does.

### 1.2 What a card is

| A card **is** | A card **is not** |
|---|---|
| One screen, scrollable at most once | A truncated article |
| The thing you need to *decide* or *not get hurt* | The thing you need to *learn* |
| Answerable in under 15 seconds | A procedure with 20 steps |
| Bengali-first with English technical terms retained | An English article with Bengali labels |
| Derived from an approved `KNW-` article and traceable to it | Independently authored content |
| Purged and replaced when its source changes | A frozen snapshot |

**`RC-01`: every card derives from an approved `KNW-` article and names it.** A card with no parent
is unreviewed content in the most trusted position in the system.

**In scope:** the pack's composition rules; card format and constraints; the three pack layers;
the non-removable safety core; currency and purge; the card inventory (§11); and the pack budget
allocation method (§12).

**Out of scope:**

| Subject | Owned by |
|---|---|
| The articles cards derive from | `KB-004`…`KB-014` |
| Article authoring standards | [`KB-002_Article_Template_and_Authoring_Standard.md`](KB-002_Article_Template_and_Authoring_Standard.md) |
| Tagging and pack scoping inputs | [`KB-001_Knowledge_Architecture_and_Tagging_Standard.md`](KB-001_Knowledge_Architecture_and_Tagging_Standard.md) §4.9 |
| Currency, suspension and retirement | [`KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md`](KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md) |
| `P02` application UI copy, navigation and error messages | `UI-012` |
| Bengali typography, numerals and font fallback | `VB-009` |
| Sync engineering, delta computation, conflict handling | `M61` T-01/T-02/T-18 · `P02` |
| Diagram extract sets from manuals | [`KB-003_Repair_Manual_Index_and_Source_Register.md`](KB-003_Repair_Manual_Index_and_Source_Register.md) §11 |
| Printed fallback packs during an outage | `SP-032` · `SP-033` §9 |

---

## 2. Safety

> ⛔ **DANGER — an abbreviated safety instruction that omits a step is more dangerous than no card
> at all.** A technician trusts a card precisely because it is short and official (hazard). A
> compressed isolation sequence, a missing discharge step, or a hazard warning trimmed for space
> can kill someone (consequence). **`RC-02`: safety cards are never compressed for space. If a
> safety procedure does not fit on a card, the card becomes a pointer to the full article and says
> so plainly** (avoidance).

> ⚠ **WARNING — a stale card is trusted absolutely.** `M61` `KPI-C61-08` sets **zero** stale
> articles served offline as the target, and cards are the most-trusted content in the pack
> (hazard). A superseded card followed in the field produces the failure the whole currency policy
> exists to prevent (consequence). **`RC-03`: cards carry their version and currency state visibly,
> and are purged on supersession** (`BRU-KMS-05`, `M61` T-03) (avoidance).

> **NOTICE — the safety core is non-removable.** §6.3 defines a set of cards that are present on
> every device regardless of scope, family or budget pressure. Pack-size optimisation may never
> remove them (`SD-07`).

---

## 3. Symptoms — *the signals that the card set is failing*

| Signal | What it indicates |
|---|---|
| Technicians photograph cards and share them in chat | The pack is not reaching them, or is out of date on their device |
| Cards opened but jobs still escalated for the same question | The card does not answer the actual question |
| The pack exceeds its budget and safety cards are proposed for removal | §6.3 is being tested — **refuse** |
| Sync failures concentrated in one branch or one device model | Connectivity or device constraint, not content |
| A card and its parent article disagree | `RC-01` traceability has broken |
| Cards consulted far less than expected against job volume | Findability inside the pack, or the card set is wrong |
| A technician says "I couldn't find it so I called" | The escalation card worked and the content card did not |
| Bengali cards read as translated English | `RC-09` failing — the card was written in English and converted |

---

## 4. Likely Causes

| # | Cause | Frequency | Confirming test |
|---:|---|---|---|
| 1 | The pack was scoped from tags that are wrong or absent | **Highest** | `KB-001` `KA-05` conformance on the source articles |
| 2 | The budget forces exclusions that are made by size rather than by value | High | Compare excluded cards against consultation demand |
| 3 | Cards written by compressing articles rather than by authoring for the medium | High | Card length distribution; reading-time test |
| 4 | Sync not running — metered connection, device storage full, app permissions | High | Pack telemetry (`KPI-C61-07`) |
| 5 | Card set never updated after the article changed | Medium | Card version vs parent article version |
| 6 | The technician's scope changed and the pack did not recompute | Medium | Assignment change vs pack recompute time |
| 7 | Bengali written as a translation rather than authored | Medium | Localisation review |
| 8 | Too many cards — the set is a library again | Medium | Card count against §12 |

---

## 5. Diagnostic Procedure — *how the pack is composed for one technician*

| Step | Input | Source | Result |
|---:|---|---|---|
| 1 | **Safety core** — every card in §6.3 | This file | Loaded first, always, regardless of budget |
| 2 | Device families the technician works | `MD-010` competency + 90-day job history | Family card layers |
| 3 | Brands certified | `MD-011` | Brand-scoped cards where they exist |
| 4 | Repair level | `MD-010` | Level-appropriate cards; L3 cards excluded for L1 |
| 5 | Hazard classes trained | `MD-011` + `M59` | Hazard cards matching what they may encounter |
| 6 | Service mode | `MD-020` — field, bench, workshop | Field technicians get the field-weighted set |
| 7 | Open S1/S2 bulletins affecting their scope | [`KB-010`](KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md) | Bulletin cards, until acknowledged and closed |
| 8 | Active known issues on their models | [`KB-011`](KB-011_Known_Issue_and_Workaround_Register.md) | Workaround cards |
| 9 | Instruments issued to them | `MD-046` | Tool cards (`KB-012`) |
| 10 | **Budget check** | §12 | If over budget, apply the §12 shedding order — **never touching step 1** |
| 11 | Diagram extracts for their top models | `KB-003` §11 | Media, budget permitting |
| 12 | Currency check | [`KB-015`](KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md) | Suspended and retired content purged (`RC-03`) |

**`RC-04`: the pack is computed, not chosen.** A technician does not curate their own pack and a
manager does not curate it for them — the only hand-curated element is which cards exist at all
(§11), and that is a category-level decision (`KA-18` exception).

---

## 6. Repair Procedure — *the card standard*

### 6.1 Format constraints

| Constraint | Rule |
|---|---|
| **Length** | One screen on a mid-range Android at default text size; **one scroll maximum** |
| **Reading time** | Answerable in **under 15 seconds** for a decision card, 60 for a procedure card |
| Structure | Title → the answer → the caveat → the escalation. **The answer is first, never last** |
| Steps | Maximum 7 numbered steps. More than 7 means it is an article, not a card |
| Images | At most one, and only where it is the answer — a connector location, a terminal layout, a warning symbol |
| Text size | Legible in sunlight at arm's length; no text smaller than the `CG-011` minimum |
| Contrast | High-contrast; **usable with a cracked or dirty screen**, which is the actual condition of many technician devices |
| Interaction | **One-handed, thumb-reachable**; no pinch-zoom required to read anything essential |
| Colour | Never the sole carrier of meaning (`CG-011`); hazard colour is paired with a signal word |
| Language | Bengali-first with English technical terms and codes retained untranslated (`AU-31`, `KA-17`) |
| Length allowance | Laid out for the **Bengali** length, which runs 20–40% longer than English (`VB-007`, `AU-32`) |
| Offline | **Fully functional with no network.** No card may depend on a live lookup — `M61` T-15 sets article open at ≤ 100 ms offline |

### 6.2 Content rules

| # | Rule | Class |
|---|---|:--:|
| **RC-01** | Every card derives from an approved `KNW-` article and names it | **H** |
| **RC-02** | Safety cards are never compressed; where they do not fit, the card points to the article and says so | **H** |
| **RC-03** | Cards carry version and currency state visibly; suspended and retired content is purged (`BRU-KMS-05`, `KB-015` §4.4) | **C** |
| **RC-04** | The pack is computed from facets, never hand-curated per technician (`KA-18`) | **H** |
| **RC-05** | **Cards are never model-specific.** A card that applies to one model belongs in the article layer; model-specific content would multiply the set beyond any budget | **H** |
| **RC-06** | Every card states **when to stop and escalate**. A card that only tells you how to proceed is incomplete | **H** |
| **RC-07** | Cards state what they do **not** cover, in one line | **H** |
| **RC-08** | Codes on cards resolve to `MD-024` / `MD-025`; **no code is minted on a card** (`KA-02`) | **H** |
| **RC-09** | **Bengali cards are authored in Bengali, not translated from English**, and are reviewed in context by a technical reviewer with the Localisation Lead (`BN-018`) | **H** |
| **RC-10** | A card changes when its parent article changes; the two never diverge in a published state | **C** |
| **RC-11** | No card contains customer-identifiable content (`AU-26`) | **H** |
| **RC-12** | No card contains a credential, a bypass, or a method of defeating a protection | **H** |
| **RC-13** | Safety and hazard cards require HSE approval (`BRU-KMS-03`) and are re-approved after Bengali authoring (`AU-06f`) | **H** |
| **RC-14** | The card set is reviewed as a **set**, not only card by card — the test is whether it covers the decisions a technician actually faces | **C** |

### 6.3 The safety core — non-removable

**Present on every device, for every technician, at every budget.** `SD-07` in
[`KB-013`](KB-013_ESD_Chemical_and_Battery_Safety_Data.md) makes this binding.

| Card | Source | Why non-removable |
|---|---|---|
| **Emergency and incident — who to call, what to do first** | `SP-030` · `M59` | The one card needed when nothing else matters |
| **Electrical isolation and proving sequence** | `KB-013` §2 · `KB-004` §2 | The most frequent fatal-risk activity |
| **Swollen or damaged battery — isolate, never charge, never refit** | `KB-013` §4 | Present in every family; the fastest-moving hazard |
| **Refrigerant class identification (A1 / A2L / A3) and what follows** | `KB-013` §5 | The hazard the workforce's habits predate |
| **ESD station shift check** | `KB-013` §3 | Cheap, daily, and invisible when skipped |
| **Hazard signal words and what they mean** | `KB-002` §4.4 | Makes every other safety block readable |
| **Stop-and-escalate triggers** | `SP-005` · `SP-033` `DT-03` | The card that ends a job safely |
| **Device identity and IMEI — the absolute prohibition** | `KB-006` §6.1 | Legal exposure, and the rule most likely to be broken in good faith |
| **Customer data — what you may and may not access** | `SP-012` · `05-04` T5 | Present on every mobile and storage job |
| **Working at height and on outdoor units — the right to refuse** | `KB-005` §2 · `SP-030` | A technician alone under pressure needs to have read it beforehand |

**Ten cards.** The set is deliberately small; a safety core that runs to forty cards is not a core.

### 6.4 The three layers

| Layer | Content | Scoped by | Budget priority |
|---|---|---|:--:|
| **1 — Safety core** | §6.3 | Nobody. Everyone gets all ten | **Never shed** |
| **2 — Universal working** | Codes, escalation, coding, checklists, tool cards for issued instruments | Role and instruments | High |
| **3 — Family and situational** | Family diagnostic summaries, workaround cards, bulletin cards, diagram extracts | Family, brand, level, live bulletins and issues | Shed first (§12) |

---

## 7. Parts

Cards do not consume parts. Two parts-related cards exist in layer 2 because the decisions they
support are made away from a desk:

| Card | Source | Decision supported |
|---|---|---|
| Substitution decision sequence | [`KB-009`](KB-009_Parts_Compatibility_and_Substitution_Notes.md) §5 | Whether a non-OEM part may be fitted on this job |
| Prohibited substitutions | `KB-009` §6.4 | The nine component classes that are never substituted |

**`RC-15`: the prohibited-substitution card is layer 2 and is never shed**, because it is a
safety control expressed as a parts rule.

---

## 8. Verification and QC

| Test | Pass criterion | Recorded in |
|---|---|---|
| Every card names an approved parent article | 100% (`RC-01`) | Weekly set integrity report |
| Safety core present on every device | **100%, no exceptions** (§6.3) | Pack telemetry |
| Card version matches parent article version | 100% (`RC-10`) | Weekly |
| Suspended and retired content absent from packs | **Zero present** (`RC-03`, `KPI-C61-08`) | Purge propagation test (`M61` AC-04) |
| Technicians with a current pack | **> 98%** (`KPI-C61-07`) | Pack telemetry |
| **Reading-time test** — decision card answered in under 15 seconds | Sampled, 20 technicians | Usability test |
| **Sunlight and one-handed legibility** | Field test on the actual device class | Usability test |
| Bengali cards authored, not translated | Sampled by the Localisation Lead | `RC-09` review |
| Cards state their escalation trigger | 100% (`RC-06`) | Content review |
| Cards state what they do not cover | 100% (`RC-07`) | Content review |
| No model-specific cards | Zero (`RC-05`) | Set review |
| Hazard cards HSE-approved, before and after Bengali | 100% (`RC-13`) | Approval record |
| Pack within budget with the safety core intact | 100% | Pack computation |
| **Offline open latency** | ≤ 100 ms (`M61` T-15) | Performance test |
| **Consultation rate on cards** | Rising; falling triggers `KB-015` `KR-20` | Usage analytics |

> **The reading-time and sunlight tests are the ones that will be skipped and should not be.**
> Every other row can be checked from a desk. These two are the only ones that test whether the
> card works in the conditions it was built for, and a card set signed off in an office is a card
> set nobody has actually used.

---

## 9. Resolution Coding

Cards carry no `MD-025` code. Two coding-relevant cards exist in layer 2, because coding is done at
the point of completion, often offline:

| Card | Purpose |
|---|---|
| **Resolution coding quick reference** | The `MD-025` `action_class` set with one line each on when to use it — `clean` and `configure` are the under-recorded ones (`TG-16`) |
| **Fault code capture** | What to capture before clearing a code (`KB-008` `FC-11`), and that `FLT-UNK` is a legitimate outcome (`SP-033` `DT-02`) |

**`RC-16`: the coding cards state that an honest unknown is acceptable.** Coding cards that imply
every job has a confident code produce fabricated codes, which is worse for the taxonomy than
blanks.

---

## 10. Escalation

| Escalate when | To | With what evidence |
|---|---|---|
| A card is wrong | **Knowledge Manager immediately**; suspend the card and its parent (`KB-015` §4.6) | The card, the version, what happened |
| A safety card is wrong or incomplete | **HSE Lead — suspend without waiting** (`KB-015` §4.6) | Same |
| A device cannot hold the pack including the safety core | **CTO — this is a device-fleet problem, not a content problem** (`O-02`) | Device model, storage, pack size |
| Pack sync failing for a technician | `R33` IT; the technician works from the last good pack with its currency marking | Sync log |
| A technician is working from a pack more than 30 days old | Branch manager + `R33`; **assignment review if it persists** | Pack telemetry |
| The safety core is proposed for reduction to fit a budget | **Refuse; escalate to HSE Lead and Quality Manager** (§6.3, `SD-07`) | The proposal |
| Cards and articles have diverged | Knowledge Manager (`RC-10`) | Both versions |
| A card is being shared outside the app | Knowledge Manager; usually a signal that the pack is not reaching people | Where it was found |
| Bengali card wording is unclear or wrong in the field | Localisation Lead with a technical reviewer; **suspend if it could mislead** | The wording, the misunderstanding |

---

## 11. Card Inventory *(addition — justified: consistent with `KB-004` §11; a pack with no enumerated membership cannot be budgeted, built or measured)*

**48 cards.** Layer 1 is fixed at ten; layers 2 and 3 are scoped per technician.

### 11.1 Layer 1 — Safety core (10, non-removable)

The ten cards in §6.3. All `P0`, all HSE-approved, all in both languages.

### 11.2 Layer 2 — Universal working (18)

| # | Card | Source | Pri |
|---:|---|---|:--:|
| 11 | Stop-and-escalate matrix — who, when, with what | `SP-005` | **P0** |
| 12 | Resolution coding quick reference | `MD-025` | P1 |
| 13 | Fault code capture — capture before clearing; `FLT-UNK` is valid | `KB-008` | P1 |
| 14 | Fault code lookup — how to use the mapping offline | [`KB-008`](KB-008_Fault_Code_Library_and_Interpretation_Guide.md) | P1 |
| 15 | **Substitution decision sequence** | [`KB-009`](KB-009_Parts_Compatibility_and_Substitution_Notes.md) §5 | P1 |
| 16 | **Prohibited substitutions — the nine classes** (`RC-15`) | `KB-009` §6.4 | **P0** |
| 17 | `part_class` and what it means for warranty and claims | `KB-009` §6.1 | P1 |
| 18 | Warranty and coverage check before disassembly | `MD-031` | P1 |
| 19 | Estimate thresholds and approvals — BDT 5,000 / 25,000 | `BRU-SRM-07`/`-08` | P1 |
| 20 | Beyond economic repair — evidence and second technician | `BRU-SRM-12` | P1 |
| 21 | Rework definition and what to do when you meet one | `BRU-SRM-06` | P2 |
| 22 | Certification check before brand warranty work | `BRU-SRM-09` | P1 |
| 23 | Evidence capture — what photographs are required and when | `DT-004` · `BRU-WTY-01` | P1 |
| 24 | Customer handover and sign-off essentials | `SP-008` · `DT-007` | P2 |
| 25 | Cash handling in the field | `SP-019` | P2 |
| 26 | Offline working — what syncs, what does not, what to do | `UI-009` · `M61` | P1 |
| 27 | Multimeter safety card — category, rating, current-range rule | [`KB-012`](KB-012_Tool_Jig_and_Test_Equipment_Operating_Guides.md) | **P0** |
| 28 | Instrument pre-use check | `KB-012` §5.1 | P1 |

### 11.3 Layer 3 — Family and situational (20)

| # | Card | Family | Source | Pri |
|---:|---|---|---|:--:|
| 29 | Laptop no-power isolation summary | `DF-IT` | `KB-004` | P1 |
| 30 | Laptop thermal service summary | `DF-IT` | `KB-004` | P2 |
| 31 | Printer jam and print-quality quick paths | `DF-IT` | `KB-004` | P2 |
| 32 | Monitor / power-board stored-energy card | `DF-IT` | `KB-004` | P1 |
| 33 | **AC not cooling — the diagnostic path in one screen** | `DF-HA` | `KB-005` | P1 |
| 34 | **Leak-before-recharge rule** (`TG-18`) | `DF-HA` | `KB-005` | **P0** |
| 35 | Refrigerant recovery and weight recording | `DF-HA` | `KB-005` · `KB-013` §5 | **P0** |
| 36 | AC installation review checklist | `DF-HA` | `KB-005` `TG-19` | P2 |
| 37 | **Microwave HV discharge — step 1, every time** | `DF-HA` | `KB-005` | **P0** |
| 38 | **Geyser earth-leakage — never repeatedly reset** | `DF-HA` | `KB-005` | **P0** |
| 39 | Washing machine leak containment | `DF-HA` | `KB-005` | P2 |
| 40 | **Mobile battery removal — adhesive method, never pry** | `DF-MB` | `KB-006` | **P0** |
| 41 | **Water resistance is not restored unless the seal procedure is followed** | `DF-MB` | `KB-006` `TG-30` | P1 |
| 42 | Liquid-damage first response and customer expectation | `DF-MB` | `KB-006` | P1 |
| 43 | Non-genuine part effects summary | `DF-MB` | `KB-006` · `KB-009` | P2 |
| 44 | **Degraded array — stop, record, verify, decide** | `DF-SRV` | `KB-007` §5.1 | **P0** |
| 45 | Backup verification before data-path work | `DF-SRV` | `KB-007` `TG-39` | P1 |
| 46 | **Access control — the mandatory egress test** | `DF-SEC` | `KB-007` §6.3 | **P0** |
| 47 | CCTV footage access and privacy rules | `DF-SEC` | `KB-007` §6.2 | P1 |
| 48 | Active bulletin and known-issue cards *(generated, not authored)* | All | `KB-010` · `KB-011` | P1 |

**Set totals:** 48 cards · 10 non-removable safety core · **13 further at `P0`** ·
**card 48 is generated from live registers rather than authored**, so its content changes without a
card-set revision (`RC-10` applies to its template, not its instances).

---

## 12. Pack Budget and Shedding Order *(addition — justified: `M61` Q-04 leaves the budget undecided, and a pack with no shedding rule will shed by accident)*

### 12.1 Allocation

| Layer | Allocation | Note |
|---|---|---|
| **Layer 1 safety core** | **Reserved first, always** | Ten text-and-symbol cards; negligible size |
| Layer 2 universal | Reserved second | Eighteen cards, text-dominant |
| Layer 3 family cards | Scoped to the technician's families | Twenty cards maximum, usually far fewer per person |
| Live bulletin and known-issue cards | Reserved — **these are time-critical** | Small, and they expire |
| **Diagram extracts** (`KB-003` §11) | **All remaining budget** | `M61` T-02: diagrams are the largest payload and the most valuable content |
| Reserve | A margin for growth between syncs | Sized by the `P02` team |

### 12.2 Shedding order — `RC-17`

When the pack exceeds budget, content is shed in this order and no other:

| Order | Shed | Never |
|---:|---|---|
| 1 | Diagram extracts for the technician's **least-worked** models | — |
| 2 | Family cards for families worked fewer than N times in 90 days | — |
| 3 | Layer 2 cards not relevant to their service mode | — |
| 4 | — | **Layer 1 safety core, prohibited-substitution card, active S1/S2 bulletin cards, active known-issue cards for their models** |

**`RC-18`: shedding is reported, never silent.** The technician sees what is not on their device
and why, and the Technical Library Owner sees the aggregate. A pack that quietly dropped the
diagrams for a model is indistinguishable, to the person holding it, from a library that never had
them.

### 12.3 The budget question

`M61` Q-04 records the per-device storage budget as an open question, given that diagrams dominate
and `P02` targets a mid-range Android with 3 GB RAM. **This file does not set the number** — it is a
device-fleet and platform decision. What it does is make the number's consequences explicit:

| If the budget is… | Then… |
|---|---|
| Generous | Layers 1–3 and a wide diagram set fit; the pack is a genuine offline library |
| Moderate | Layers 1–3 fit comfortably; diagram extracts are scoped to the top models |
| Tight | Layers 1–2 and scoped family cards fit; diagrams become on-demand-with-caching, and **`P02`'s stated offline diagram capability is not met** |
| Very tight | **The `P02` non-negotiable requirement for offline repair manuals and diagrams cannot be delivered as specified**, and that must be escalated as a scope matter, not absorbed as a content compromise |

**`RC-19`: if the budget cannot hold the safety core plus layer 2, the problem is the device fleet,
not the content.** Escalate to CTO (§10).

---

## 13. Related Documents *(addition — justified: category convention)*

| Document | Relationship |
|---|---|
| [`KB-001_Knowledge_Architecture_and_Tagging_Standard.md`](KB-001_Knowledge_Architecture_and_Tagging_Standard.md) | §4.9 pack scoping inputs; `KA-18` names this set as the curated exception |
| [`KB-002_Article_Template_and_Authoring_Standard.md`](KB-002_Article_Template_and_Authoring_Standard.md) | Parent-article standard; §4.4 signal words |
| [`KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](KB-013_ESD_Chemical_and_Battery_Safety_Data.md) | `SD-07` non-removability; the source of five safety-core cards |
| [`KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md`](KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md) | Purge, suspension and the 6-month card cycle |
| [`KB-003_Repair_Manual_Index_and_Source_Register.md`](KB-003_Repair_Manual_Index_and_Source_Register.md) | §11 diagram extracts — the budget's dominant consumer |
| [`KB-008_Fault_Code_Library_and_Interpretation_Guide.md`](KB-008_Fault_Code_Library_and_Interpretation_Guide.md) · [`KB-009_Parts_Compatibility_and_Substitution_Notes.md`](KB-009_Parts_Compatibility_and_Substitution_Notes.md) · [`KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md`](KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md) · [`KB-011_Known_Issue_and_Workaround_Register.md`](KB-011_Known_Issue_and_Workaround_Register.md) · [`KB-012_Tool_Jig_and_Test_Equipment_Operating_Guides.md`](KB-012_Tool_Jig_and_Test_Equipment_Operating_Guides.md) | Card sources |
| [`KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md`](KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md) · [`KB-005_Troubleshooting_Guide_Set_Home_Appliance.md`](KB-005_Troubleshooting_Guide_Set_Home_Appliance.md) · [`KB-006_Troubleshooting_Guide_Set_Mobile_and_Tablet.md`](KB-006_Troubleshooting_Guide_Set_Mobile_and_Tablet.md) · [`KB-007_Troubleshooting_Guide_Set_Server_Network_and_CCTV.md`](KB-007_Troubleshooting_Guide_Set_Server_Network_and_CCTV.md) | Layer 3 parents |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md) | Trees are the other half of the offline pack; §9 printed fallback |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md) | Emergency card source |
| `UI-012` `P02` Technician App UI Copy Pack | The application the cards live in |
| `VB-009` Bengali Typography and Brand Standard · [`../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) | Legibility and accessibility constraints in §6.1 |
| `TR-009` Course Pack — Field Technician · `TR-022` Job Aid and Quick Reference Library | **Overlap risk — see `O-05`** |

---

## Sources and Currency

| Source | Verified | Next review |
|---|---|---|
| `04-00` `P02` — 24-hour offline operation; offline repair manuals, wiring diagrams and past repair notes; complete Bengali UI including error messages | 2026-08-16 | 2027-02-16 |
| `M61` §5.2 FR-KMS-017/018; §6 T-01, T-02, T-03, T-15; §9 `BRU-KMS-05`; §15 `KPI-C61-07`, `KPI-C61-08`; §18 Q-04 | 2026-08-16 | 2027-02-16 |
| `05-05` §2 `BRU-SRM-06`, `-07`, `-08`, `-09`, `-12`; `BRU-WTY-01` | 2026-08-16 | 2027-02-16 |
| `MD-010`, `MD-011`, `MD-020`, `MD-024`, `MD-025`, `MD-031`, `MD-046` | 2026-08-16 | 2027-02-16 |
| `VB-007` — Bengali labels run 20–40% longer than English | 2026-08-16 | 2027-02-16 |

> **No card content is written in this file.** The forty-eight cards are deliverables authored
> against §6.1 and §6.2 and derived from approved articles (`RC-01`). Drafting card wording here
> would create a second, unversioned copy of content that must have exactly one source — the
> `CP-01` violation this whole category is built to avoid.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The 48 cards are unwritten, and 33 of their parent articles are also unwritten.** Cards cannot precede their parents (`RC-01`). The ten safety-core cards are the exception worth making: they derive from `KB-013`, `SP-030` and `SP-033`, which can be authored first | Content Design with Technical Director and HSE Lead | **The 10 safety-core cards before W2 `P02` release** |
| **O-02** | **The per-device storage budget remains undecided** (`M61` Q-04). §12.3 states the consequences at each level, including the level at which a `P02` non-negotiable requirement cannot be met. **This is a scope decision, not a content decision** | CTO with Operations Director | **Before W2 `P02` build** |
| **O-03** | Card 48 — live bulletin and known-issue cards — is **generated from registers that do not yet exist** (`KB-010` `O-01`, `KB-011` `O-02`). The generation template can be designed now; the content arrives with the registers | `P02` team with Knowledge Manager | W4 |
| **O-04** | **The reading-time, sunlight and one-handed tests in §8 need a defined method and a device sample.** They are the tests most likely to be skipped and the only ones that check the medium | Content Design with `P02` team | **W2 — before the card set is signed off** |
| **O-05** | **Overlap risk with `TR-022` Job Aid and Quick Reference Library.** `TR-022` provides one-page task references for the twenty most frequent tasks per role; this file provides offline field cards. For a field technician these could be the same artefact produced twice by two workstreams — a direct `CP-01` violation. **The boundary is not defined in either register row.** Raised as audit finding **KB-08** | Programme Content Lead with L&D and Content Design | **W1 — before either is authored** |
| **O-06** | Bengali card authoring (`RC-09`) requires authors who can write technical Bengali natively, not translators. `KB-002` `O-05` records the terminology gap; this adds an authoring-capability gap | Localisation Lead with Technical Director | **W2** |
| **O-07** | Printed fallback for the card set during an outage or on a failed device is not specified. `SP-032` and `SP-033` §9 establish the printed-pack pattern; the card set should follow it | Operations with Content Design | W3 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Knowledge_Article.md`; additions §11–§13 justified
- [x] The case for curation over caching argued from the five real constraints, not asserted
- [x] Card defined against what it is not, so authors do not produce truncated articles
- [x] Every card required to derive from an approved parent article (`RC-01`)
- [x] Safety cards protected from compression (`RC-02`) and the safety core made non-removable
- [x] Format constraints stated for the actual conditions — sunlight, one hand, cracked screens, Bengali length
- [x] Bengali required to be **authored**, not translated (`RC-09`)
- [x] Pack computed from facets, not curated per technician (`RC-04`)
- [x] Card inventory enumerated — 48 cards across three layers with sources and priorities
- [x] Shedding order defined so that budget pressure cannot silently remove safety content (`RC-17`, `RC-18`)
- [x] The budget question's consequences stated, including the point at which a `P02` non-negotiable fails
- [x] Model-specific cards prohibited to keep the set bounded (`RC-05`)
- [x] Every card required to state its escalation trigger and its limits (`RC-06`, `RC-07`)
- [x] All internal links resolve
- [x] `BRU-KMS-*` and `KPI-C61-*` cited to `M61`; `BRU-SRM-*`, `BRU-WTY-*` cited to `05-05`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` the 10 safety-core cards authored — outstanding; needed before `P02` release**
- [ ] **`O-02` storage budget decided — outstanding; a scope decision**
- [ ] **`O-05` `TR-022` boundary resolved — outstanding; duplication risk**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Technical Director and Content Design Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
