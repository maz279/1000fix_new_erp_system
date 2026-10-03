---
id: BN-018
title: Localisation QA and Linguistic Sign-off Checklist
project: 1000FiX ERP System v2.0
content_type: Checklist
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Localisation Lead
author: Localisation with Content Design and QA
reviewers: [Programme Content Lead, Content Design Lead, QA Lead, Legal & Compliance, Platform Engineering, Accessibility reviewer]
approver: Programme Content Lead
content_class: E
purpose: >
  Defines gate G4 in operational terms: who reviews, against what, in what context, what counts
  as a defect, what blocks approval, and what evidence is recorded. Translation reviewed as a
  list of strings passes review and fails in production, because the reviewer cannot see
  truncation, cannot see which button the label sits on, and cannot see that two different
  English strings were given the same Bengali. CG-008 B-09 makes in-context sign-off unwaivable
  for customer- and field-facing bilingual content; this file is how that sign-off is actually
  performed and proved.
traces_to: [CG-007 G4, CG-007 §3.4, CG-007 §5, CG-008 U-42, CG-008 U-43, CG-008 U-44, CG-008 U-45, CG-008 U-46, CG-008 U-47, CG-008 U-48, CG-008 B-09, CG-010 §10, CM-R6, BN-002, BN-003, BN-004, BN-005, BN-006, BN-007, BN-008 §7, TS-016]
priority: P1
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/00_Content_Governance_and_Standards/CG-007 §3.4 G4 Linguistic — accuracy, register, terminology, in-context, layout, formatting; 5 working days after English approval; reviewer independent of the translator (CO-05); "in-context review is not optional… BN-018 defines the mechanics"
    verified: 2026-08-17
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-008 §3.8 U-42…U-48 bilingual checklist items and §5 B-09 — customer- and field-facing bilingual in-context sign-off is never waivable (WV-03)
    verified: 2026-08-17
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-010 §10 verification table and CM-R6 — a bilingual file is not Approved until the Bengali counterpart has passed in-context linguistic sign-off
    verified: 2026-08-17
    class: P1
  - source: MQM error typology and scoring — seven dimensions, severity levels, and a linear scoring model; typical weighting of 5 for major and 1 for minor
    verified: 2026-08-17
    class: P2
supersedes: none
review_due: 2027-02-17
---

# BN-018 — Localisation QA and Linguistic Sign-off Checklist

> **`CG-007` §3.4 states the requirement and names this file for the mechanics.** This is that
> file.
>
> **The central rule, and the reason the gate exists at all:** a translation reviewed as a
> spreadsheet of strings passes review and fails in production. The reviewer cannot see that the
> label is 40% too wide for its button, cannot see that the confirmation dialog's Bengali reads as
> the opposite of the action, and cannot see that `common.action.approve` and
> `common.action.confirm` were given the same Bengali word.
>
> **None of those defects is a translation error.** Every one of them is invisible until the
> Bengali is looked at where it lives.

---

## 1. What G4 is, and what it is not

| G4 is | G4 is not |
|---|---|
| A **review of the Bengali in the place it will appear** | A proofread of a bilingual file |
| Performed by a **linguist independent of the translator** | Performed by the translator, or by the author |
| A **gate** — it blocks `Approved` | A quality score to be improved later |
| Concerned with **meaning, register, terminology, layout and format** | Concerned only with grammar |
| Evidenced and retained | Asserted in a status column |

| # | Rule |
|---|---|
| **QA-01** | **G4 applies to all bilingual files** (`CG-007` §3.4) |
| **QA-02** | **For customer- and field-facing content, in-context sign-off is never waivable** (`CG-008` `B-09`, `WV-03`, `PS-03`, `P02` non-negotiable #3) |
| **QA-03** | **G4 runs after English approval**, with a service level of **5 working days** (`CG-007` §6) |
| **QA-04** | **The wave gate is set by the G4 date, not the English approval date** (`CG-007` §5, `CG-010` §9, `BN-001` `WG-04`) |
| **QA-05** | **A file that has not passed G4 is `Draft`**, whatever its English status. The pair moves together (`CM-R6`, `LC-08`) |
| **QA-06** | **G4 is not a substitute for the MQM measurement in `BN-008` §7, and the measurement is not a substitute for G4.** The measurement finds translation defects; the gate finds context defects |

---

## 2. Who reviews

| # | Rule |
|---|---|
| **RV-Q1** | The linguistic reviewer is **a native Bengali speaker, resident in Bangladesh, familiar with the domain** |
| **RV-Q2** | The reviewer is **independent of the translator** (`CO-05`). The same person may not translate and sign off, in any circumstance |
| **RV-Q3** | **At least two Bengali resources are therefore required**, which is a resourcing statement, not an aspiration (`CG-010` §9) |
| **RV-Q4** | **Class A and B content requires a reviewer with legal-Bengali experience** (`BN-002` §13 item 3) |
| **RV-Q5** | **`P02`, `P09` and `P11` require an additional review by a serving user** — a technician, a rider, an auditor — on the device, at their place of work. Register-correct Bengali that field users do not say is still wrong |
| **RV-Q6** | **Voice content requires a listening review, not a reading review** (`BN-017` `VF-01`) |
| **RV-Q7** | **Statutory documents require G6 external verification of the Bengali**, not only the English (`BN-015` `ST-B04`) |
| **RV-Q8** | The reviewer's **name is recorded** in the sign-off block. Anonymous sign-off is not sign-off |

---

## 3. What "in context" means, per surface

**The single most-avoided requirement in localisation, because it is the most inconvenient.**

| Surface | In context means | Not acceptable |
|---|---|---|
| Web portal | **The running build**, at 1366×768 and at mobile width, in Bengali | A screenshot set; a Figma frame |
| **`P02`, `P09`, `P11`** | **The application, on a mid-range Android 11 device with 3 GB RAM**, outdoors where the content is used outdoors | An emulator; a high-end handset |
| `P01` app | Android **and** iOS, low and high density | One platform |
| Notification — SMS | **A real message on a real handset**, including a feature phone | A preview pane |
| Notification — push | **The notification shade**, where the system font renders it (`BN-014` `PU-01`) | In-app preview |
| Notification — email | **Gmail Android, Gmail web, Outlook desktop, Apple Mail iOS** (`VB-009` §7) | One client |
| Notification — WhatsApp | The **approved template** in the WhatsApp client | The submission form |
| Document — A4 | **Printed, on a supported printer model** | A PDF on screen |
| Document — thermal | **Printed on the certified thermal model** (`BN-015` `TH-05`) | A4 proof |
| Voice | **A real phone call over a real network** (`BN-017` `VF-02`) | A local audio file |
| Help and training | **On the device the learner uses**, alongside the surface it describes | A document review |
| Master data columns | **Rendered in the screen that displays them** (`BN-003` `MD-B2`) | The CSV |
| Reports | **The rendered report and its export**, opened in Excel (`BN-012` `AN-04`) | The definition |

| # | Rule |
|---|---|
| **CT-Q1** | **A review performed outside its context row above is not a G4 review** and does not satisfy `B-09` |
| **CT-Q2** | Where no build exists, **G4 cannot be performed** and the file remains `Draft`. This is a schedule fact, not a process failure — and it is why `G3` and `G4` are sequenced as they are (`CG-007` `SL-02`) |
| **CT-Q3** | The reviewer must be able to **exercise the states**, not only view the happy path: empty, error, loading, offline, conflict, permission-denied, zero-count |

---

## 4. The checklist

Every item is answered **yes** before sign-off. A **no** is a defect, classified per §5.

### 4.1 Accuracy — `LQ-01` … `LQ-05`

| # | Check | Reference |
|---|---|---|
| **LQ-01** | The Bengali says what the English says — **no addition, no omission, no softening** | `CG-007` §3.4 |
| **LQ-02** | **No obligation, price, date, quantity or legal position is changed** by the Bengali | `BN-002` `TN-08` |
| **LQ-03** | **Every placeholder present in the English is present in the Bengali**, with the same name | `BN-005` `BE-04` |
| **LQ-04** | Bangla Academy spelling throughout; the Bengali spell check has been run | `BN-002` `OR-01`, `OR-03` |
| **LQ-05** | **Nothing is machine-translated.** A translator attestation is on file | `CG-010` MT-01, `BN-008` `SU-07` |

### 4.2 Register and voice — `LQ-06` … `LQ-10`

| # | Check | Reference |
|---|---|---|
| **LQ-06** | **চলিত register throughout; no সাধু, no dialect** | `BN-002` `RD-A`, `RD-B`, `RD-D` |
| **LQ-07** | **আপনি and honorific verb forms only. No তুমি, no তুই** | `BN-002` `AD-01`, `AD-03` |
| **LQ-08** | The Bengali **sounds like something a Bangladeshi would say**, not like a rendering of English word order | `BN-002` `SC-01`, `SC-02` |
| **LQ-09** | **No error makes the user the agent of the failure**; every error names a remedy | `BN-002` `TN-01`, `TN-04` |
| **LQ-10** | The **Class A/B formal sub-register** is used where it applies, and **not** on UI surfaces | `BN-002` `RD-C`, `FR-02` |

### 4.3 Terminology — `LQ-11` … `LQ-15`

| # | Check | Reference |
|---|---|---|
| **LQ-11** | **One English term → one Bengali form, and one Bengali form → one English term.** Checked **both ways** across the whole surface | `BN-003` `GL-01`, `GL-02` |
| **LQ-12** | **Help, training, SOP and document text quotes the exact bundle string** for any UI control it names | `BN-016` `HC-B01` |
| **LQ-13** | **Do-not-translate items are untranslated and untransliterated** | `BN-004` `DN-01`, `DN-02` |
| **LQ-14** | The **loanword tier** used matches `BN-003` — no English verb + করুন where a Tier 3 term exists | `BN-002` `LW-04` |
| **LQ-15** | **Status labels are quoted from `MD-027`**, in the correct column for the surface | `BN-003` `ST-01`, `ST-02` |

### 4.4 Format — `LQ-16` … `LQ-20`

| # | Check | Reference |
|---|---|---|
| **LQ-16** | **Numerals follow `BN-007` §3** — Arabic by default, Bengali only in the declared prose contexts, never mixed within a value, column, document, message or screen region | `BN-007` `NM-A`…`NM-C` |
| **LQ-17** | **Money: Arabic digits, `৳` prefix, two decimals, lakh/crore grouping** | `BN-007` `FM-07`, `FM-09` |
| **LQ-18** | **Dates `dd/MM/yyyy` in data; Bengali month names in prose; never `MM/DD/YYYY`** | `BN-007` `FM-11`, `FM-12` |
| **LQ-19** | **Times use Bengali day-period words, never `AM`/`PM`**; dense surfaces use 24-hour | `BN-007` `FM-20`, `FM-21` |
| **LQ-20** | **Working-day and due-date wording reflects the Friday–Saturday weekend** | `BN-007` `BD-01`, `FM-26` |

### 4.5 Layout and rendering — `LQ-21` … `LQ-27`

| # | Check | Reference |
|---|---|---|
| **LQ-21** | **No truncation, no overflow, no clipped matra**, at the target size on the target device | `BN-006` `LB-07`, `LB-10` |
| **LQ-22** | **Conjuncts render as formed conjuncts** — the `BN-006` §9 test set has been run on this surface | `BN-006` `RV-01` |
| **LQ-23** | **Bengali is at or above its floor**; nothing is condensed, letter-spaced or synthetically bolded | `VB-009` `MS-01`, `BN-006` `SZ-05`, `SZ-06` |
| **LQ-24** | **Line height is set per language**; Bengali text is not justified | `VB-009` `LH-01`, `LH-04` |
| **LQ-25** | **Latin inside Bengali renders in Inter, one step smaller, on the same baseline** | `VB-009` `MX-02`, `MX-03` |
| **LQ-26** | **Layout holds at 200% zoom and under WCAG text-spacing adjustment** | `VB-009` `AC-04`, `AC-05` |
| **LQ-27** | **Verified on the rank-2 fallback face as well as rank 1** | `VB-009` `MM-04` |

### 4.6 Completeness — `LQ-28` … `LQ-33`

| # | Check | Reference |
|---|---|---|
| **LQ-28** | **100% of the surface's user-visible strings are Bengali.** Not 99% | `CG-010` `BP-05`, `BN-001` `LS-04` |
| **LQ-29** | **Empty, error, loading, offline, conflict, permission-denied and zero-count states are covered**, not only the happy path | `CG-010` §5, `CT-Q3` |
| **LQ-30** | **Accessible names, live-region text and screen-reader-only strings are Bengali** | `CG-011` BA-04, `BN-011` `AY-01` |
| **LQ-31** | **Third-party component strings** — date pickers, map controls, payment widgets, file uploaders — are Bengali or are declared as a known limitation | `CG-010` §5 |
| **LQ-32** | **Notification subject and preview text, PDF metadata and file-name-adjacent text are Bengali** where the surface is | `CG-010` §5, `BN-015` `DB-13` |
| **LQ-33** | **Null and placeholder values** — "N/A", "—", "0" — are Bengali or are a deliberate symbol | `BN-012` `AN-02`, `BN-013` `AU-02` |

### 4.7 Pair integrity — `LQ-34` … `LQ-37`

| # | Check | Reference |
|---|---|---|
| **LQ-34** | **The `_BN` counterpart exists and shares the stem**, or the file is declared a Bengali artefact | `CG-008` U-42, `CG-005` §5 |
| **LQ-35** | **English and Bengali carry the same version number** | `CG-008` U-48, `LC-08` |
| **LQ-36** | **Changes to the English since the last G4 have been re-reviewed**, not assumed unchanged | `CG-007` §7 |
| **LQ-37** | **Approved segments have been written to the TM, and only approved segments** | `BN-008` `TM-06` |

---

## 5. Defect classification

Aligned to `BN-008` §7 so that one taxonomy serves both the gate and the measurement.

| Severity | Definition | Effect on the gate |
|---|---|---|
| **Critical** | Changes the meaning of an obligation, a price, a safety instruction or a legal position; makes a statutory output non-compliant; or leaves a customer- or field-facing surface below 100% | **Gate fails. No offsetting** |
| **Major** | Would mislead or block a user; wrong term; wrong register; truncation on a primary control | **Gate fails** unless remediated before sign-off |
| **Minor** | Noticeable but does not mislead; inconsistent but comprehensible | Recorded; **must be zero at the wave gate** |

| # | Rule |
|---|---|
| **DF-01** | **Any Critical fails the gate**, regardless of the MQM score (`BN-008` `QM-02`) |
| **DF-02** | **A `LQ-28` failure is Critical by definition.** Partial bilingualism is worse than none (`BP-05`) |
| **DF-03** | **A `LQ-11` collision is Major at minimum** — two English terms sharing one Bengali form destroys a distinction the vocabulary exists to make, and one of them is usually an audit control (`BN-003` §9) |
| **DF-04** | **A `LQ-21` truncation on a safety, financial or custody string is Critical** |
| **DF-05** | Defects are recorded against the **dimension** (`BN-008` §7.1), so that trends identify the cause — briefing, terminology, source clarity or linguist |

---

## 6. Sign-off record

Stored with the content, per `CG-007` §4.2, and referenced from the file's front matter.

```yaml
linguistic_signoff:
  gate: G4
  file: BN-010_Bengali_String_Bundle_P02_Technician.md
  surface: P02
  english_version: 1.0
  bengali_version: 1.0
  reviewed_in_context: true
  context: "P02 build 2026.11.3 on Xiaomi Redmi 12, Android 11, 3 GB RAM, outdoors"
  states_exercised: [happy, empty, error, offline, conflict, permission_denied, zero_count]
  reviewer: <named linguist>
  reviewer_independent_of_translator: true
  additional_reviewers:
    - role: serving technician
      name: <named>
    - role: HSE Lead
      name: <named>
  translator_attestation_no_mt: true
  defects:
    critical: 0
    major: 0
    minor: 2
  mqm_score: 1.4
  checklist_version: BN-018 v1.0
  date: <YYYY-MM-DD>
  outcome: PASS
```

| # | Rule |
|---|---|
| **SO-01** | **`reviewed_in_context: true` with no `context:` string is not a record.** The context is what makes the claim checkable |
| **SO-02** | **`states_exercised` is enumerated**, so that a happy-path-only review is visible as one |
| **SO-03** | **The reviewer is named.** `CO-04` prohibits self-approval and it cannot be checked without a name |
| **SO-04** | Records are retained with the content and are in scope for `LG-009` retention |
| **SO-05** | The **wave audit samples sign-off records**, not only files (`AUDIT_Checklist_Recurring` E5) |

---

## 7. Failure and rework

| # | Rule |
|---|---|
| **FR-Q1** | **A failed gate returns the file to `Draft`**, not to a "conditionally approved" state, which does not exist (`CG-006`) |
| **FR-Q2** | **Rework is re-reviewed in context.** A fix verified in a spreadsheet has not been verified |
| **FR-Q3** | **Where the defect is in the English** — ambiguity, a concatenated string, an over-tight budget — **the English is fixed and re-approved.** Translating around a bad source hides the defect in the language nobody on the programme reads (`BN-002` `TX-03`) |
| **FR-Q4** | **Where the defect is a layout constraint, it is a design conversation**, not an instruction to shorten the Bengali (`VB-006` §8, `BN-006` `SZ-02`) |
| **FR-Q5** | Repeated defects of one dimension trigger a **briefing review**, not a linguist change. A rising query rate and a rising defect rate usually have the same cause (`BN-008` §10) |
| **FR-Q6** | **A gate may not be passed under schedule pressure with a remediation promise.** `B-09` is unwaivable and `WV-03` names it |

---

## 8. Sampling and audit

| Content class | G4 coverage | MQM sampling (`BN-008` `QM-04`) |
|---|---|---|
| **A** Statutory | **100%**, plus G6 external verification of the Bengali | 100% |
| **B** Legal | **100%**, plus G5 legal review of the Bengali | 100% |
| **C** Operational-critical | **100%** | 10%, 20% for a new linguist |
| **D** User-facing | **100%** | 10%, 20% for a new linguist |
| **E** Internal governance | Where bilingual, 100% | 10% |

| # | Rule |
|---|---|
| **SA-01** | **G4 coverage is always 100% of the surface.** Sampling applies to the **measurement**, never to the gate |
| **SA-02** | The wave audit re-checks a sample of **passed** surfaces, to test whether the gate is being applied or asserted |
| **SA-03** | Terminology conformance is scanned automatically every commit and sampled at G4 — target defect rate **under 2%** (`CG-004` §9) |

---

## 9. What automation catches, and what it cannot

**Stated explicitly, so that a green build is not mistaken for a passed gate.**

| Caught automatically | Only found in context |
|---|---|
| Missing key, orphan key (`BE-01`, `BE-02`) | Truncation on the actual control |
| Placeholder mismatch (`BE-04`) | A label that is correct but wrong for its button |
| Missing `=0` plural branch (`BE-05`) | Two English terms given one Bengali form |
| Ordinal category count (`BE-06`) | Register drift across a surface |
| Bengali script in a key (`BE-07`) | A confirmation whose Bengali reads as the opposite action |
| NFC normalisation (`BE-09`) | A conjunct that breaks on this device |
| Missing context note (`BE-10`) | Bengali that is grammatical and unnatural |
| Tier 1 item transliterated (`BE-11`) | A number that is correct and unreadable at 15px |
| Budget exceeded (`BE-12`) — **as a warning** | Whether exceeding it actually matters here |
| `en` = `bn` string (`BE-13`) | A place name pronounced wrongly in a recording |
| Term collision candidates (`BE-14`) | Whether the collision is real |

| # | Rule |
|---|---|
| **AU-Q1** | **A clean automated run is a precondition for G4, not a substitute for it.** The reviewer starts from a green build |
| **AU-Q2** | **A `BE-12` budget warning must be resolved or explicitly accepted at G4**, with the acceptance recorded |

---

## 10. Related documents

| Document | Relationship |
|---|---|
| [`../00_Content_Governance_and_Standards/CG-007_Review_Approval_and_Signoff_Workflow.md`](../00_Content_Governance_and_Standards/CG-007_Review_Approval_and_Signoff_Workflow.md) | §3.4 G4, which names this file |
| [`../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md) | U-42…U-48 and `B-09` |
| [`../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) | §5 coverage per surface, §10 verification |
| [`BN-002_Bengali_Translation_Standard.md`](BN-002_Bengali_Translation_Standard.md) | What §4.2 checks against |
| [`BN-003_Bilingual_Terminology_Glossary.md`](BN-003_Bilingual_Terminology_Glossary.md) | What §4.3 checks against |
| [`BN-006_Bengali_Typography_Font_and_Numeral_Standard.md`](BN-006_Bengali_Typography_Font_and_Numeral_Standard.md) | §9 test set used at `LQ-22` |
| [`BN-007_Date_Time_Number_Currency_and_Address_Formats.md`](BN-007_Date_Time_Number_Currency_and_Address_Formats.md) | What §4.4 checks against |
| [`BN-008_Translation_Memory_and_Term_Base_Management.md`](BN-008_Translation_Memory_and_Term_Base_Management.md) | The MQM taxonomy §5 aligns to; `TM-06` |
| [`../13_Test_and_Acceptance_Content/`](../13_Test_and_Acceptance_Content/) | `TS-016` accessibility, `TS-015` field conditions |

---

## 11. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-17 | Initial issue. G4 defined operationally with what it is and is not; eight reviewer rules including serving-user review for field surfaces and listening review for voice; **"in context" defined per surface with the unacceptable alternative named in each row**; a 37-item checklist across accuracy, register, terminology, format, layout, completeness and pair integrity; defect classification aligned to the `BN-008` MQM taxonomy with four automatic-Critical rules; a sign-off record schema that makes the in-context claim checkable; rework rules that push source defects back to the English; **an explicit statement of what automation cannot catch**, so a green build is not mistaken for a passed gate | Programme Content Lead (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] G4 defined operationally, not restated from `CG-007`
- [x] Reviewer independence stated with its resourcing consequence
- [x] **"In context" defined per surface, with the unacceptable substitute named in every row**
- [x] Checklist items each carry a reference to the standard they enforce
- [x] Defect severities aligned to `BN-008` §7, with the automatic-Critical cases named
- [x] Sign-off record schema specified so the in-context claim is checkable, not assertable
- [x] Rework rules push source-language defects back to the English rather than around them
- [x] Sampling separated from coverage — the gate is never sampled
- [x] **What automation cannot catch stated explicitly**
- [x] All internal links resolve
- [x] Bengali counterpart — n/a; internal governance, English-only by `CG-010` §3.2
- [ ] **`BN-018` must be available at W1**, before the first bundle is signed off — **outstanding**; it is registered at W2 while `BN-011` is W1 (`AUDIT-012` **BN-02**)
- [ ] Second Bengali reviewer resourced (`RV-Q3`) — outstanding
- [ ] Legal-Bengali reviewer identified (`RV-Q4`) — outstanding
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
