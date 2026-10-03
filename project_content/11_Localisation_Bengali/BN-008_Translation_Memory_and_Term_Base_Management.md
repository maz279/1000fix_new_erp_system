---
id: BN-008
title: Translation Memory and Term Base Management
project: 1000FiX ERP System v2.0
content_type: Standard
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Localisation Lead
author: Localisation with Procurement, Platform Engineering and Legal
reviewers: [Programme Content Lead, Procurement, Legal & Compliance, Platform Engineering, Security, Finance]
approver: Programme Content Lead
content_class: E
purpose: >
  Establishes the translation memory, term base and do-not-translate assets as company-owned,
  standards-based, versioned content assets, and fixes who may write to them, when, on what
  quality evidence, and what happens to them when a supplier relationship ends. Nine waves of
  translation across 267 bilingual files without a shared memory means paying repeatedly for the
  same strings and receiving a different Bengali answer each time. It also means that if the
  translation supplier changes in month 20, the programme starts from zero — because the leverage
  lives in the supplier's tool, not in ours.
traces_to: [CG-006, CG-010 §9, CG-013 CR-04, BN-002, BN-003, BN-004, BN-005 CX-03, BN-018, AF-09, 05-06 NFR-086]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: TMX 1.4b — the current Translation Memory eXchange specification (2005), an XML format for exchanging translation memory between CAT and localisation tools
    verified: 2026-08-17
    class: P2
  - source: TBX — TermBase eXchange, ISO 30042:2019, XML format for terminology interchange; framework provided by ISO 12620, ISO 12200 and ISO 16642
    verified: 2026-08-17
    class: P2
  - source: XLIFF — OASIS XML Localization Interchange File Format; XLIFF 2.0 adopted as ISO 21720:2017; 2.1 is the current OASIS version
    verified: 2026-08-17
    class: P2
  - source: MQM (Multidimensional Quality Metrics) — seven top-level error dimensions (Terminology, Accuracy, Linguistic conventions, Style, Locale conventions, Audience appropriateness, Design and markup) with severity levels and a scoring model; typical penalty weighting of 5 for major and 1 for minor
    verified: 2026-08-17
    class: P2
  - source: project_content/00_Content_Governance_and_Standards/CG-010 §9 — BN category estimated 180–280 person-days, volume-driven; G4 service level 5 working days; reviewers must be independent of translators (CO-05)
    verified: 2026-08-17
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-013 CR-04 — "Translation capacity cannot meet 266 bilingual files across nine waves", rated High
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# BN-008 — Translation Memory and Term Base Management

> **The translation memory is the only content asset in this programme that appreciates.**
>
> Every other file is written once and maintained. The TM gets more valuable with every wave —
> and it is also the only content asset that is routinely left in a supplier's tool, discovered
> to be unrecoverable at the moment the supplier changes, and rebuilt at full cost.
>
> `CG-013` `CR-04` already rates translation capacity as a **High** programme risk. Leverage is
> the only lever that reduces the volume side of that risk, and leverage does not happen by
> accident.

---

## 1. Purpose

| | |
|---|---|
| **What this governs** | The TM, term base and do-not-translate assets: ownership, format, structure, who writes, when, on what evidence, how leverage and quality are measured, and exit |
| **What it does not govern** | How Bengali is written (`BN-002`); which term is approved (`BN-003`); the review itself (`BN-018`); commercial rates (Procurement) |
| **What breaks without it** | The same string paid for five times with four different answers; a supplier change that resets the programme; and no evidence for whether translation quality is improving or getting worse |

---

## 2. The assets

| Asset | What it holds | Format | Owner |
|---|---|---|---|
| **TM** — translation memory | Every approved English–Bengali segment pair, with metadata | **TMX 1.4b** for interchange; native format in the tool | Localisation Lead |
| **TB** — term base | Every `BN-003` term, plus the ~4,000 master-data display values | **TBX (ISO 30042:2019)** | Localisation Lead with Enterprise Architecture |
| **DNT list** | Every `BN-004` Tier 1 item | TBX entries flagged non-translatable | Localisation Lead |
| **Style guide package** | `BN-002` plus the `VB-002` tone rows relevant to the batch | PDF/Markdown | Localisation Lead |
| **Context package** | Context notes, screenshots, budgets, placeholder documentation (`BN-005` §5) | Bundled with the XLIFF | Content author |
| **Query log** | Every translator query and its answer | Register | Localisation Lead |
| **Bilingual review record** | G4 sign-off evidence per surface | `BN-018` §7 | Localisation Lead |

| # | Rule |
|---|---|
| **TM-01** | **All seven assets are 1000FiX property.** They are content under `CG-006`, versioned, backed up and retained with the rest of the content set |
| **TM-02** | **Interchange formats are open standards** — TMX, TBX, XLIFF. A supplier's proprietary format may be used *in addition*, never *instead* |
| **TM-03** | **The authoritative copy lives in 1000FiX-controlled storage**, not in a supplier's cloud tenancy. Where a supplier's tool is the working environment, a **full standards-format export is taken at every wave boundary and on demand** |
| **TM-04** | The TM and TB are **CONFIDENTIAL — Internal Use Only**, like the content they derive from |
| **TM-05** | Context notes travel **with** the segment, through extraction, translation, review and back into the TM (`BN-005` `CX-03`). A TM segment without its context note is a future defect |

---

## 3. Supplier terms

**These clauses belong in the contract, not in a working assumption.** Procurement owns the
contract; Localisation owns these requirements.

| # | Requirement |
|---|---|
| **SU-01** | **1000FiX owns all TM and TB content**, including segments produced by the supplier, in perpetuity and irrevocably |
| **SU-02** | **Export on demand** in TMX and TBX, in full, at no charge, within 5 working days |
| **SU-03** | **Full export at every wave boundary**, unprompted (`TM-03`) |
| **SU-04** | **No reuse** of 1000FiX TM or TB content for any other client, and no contribution to a shared or public memory |
| **SU-05** | **No machine-translation training** on 1000FiX content, and no submission of 1000FiX content to a third-party MT or LLM service without written authorisation (`CG-010` MT-01, `05-06` NFR-086) |
| **SU-06** | **Translator and reviewer must be different people** (`CO-05`), evidenced per batch |
| **SU-07** | **Machine-translation attestation per batch** — a named statement that the delivery is not machine output or post-edited machine output (`CG-010` MT-03) |
| **SU-08** | **Named linguists.** The programme knows who translated and who reviewed each batch; substitution is notified |
| **SU-09** | **On exit**: full export, written confirmation of deletion from the supplier's systems, and no retention of derived assets |
| **SU-10** | **Confidentiality and data handling** consistent with `LG-006` and `05-06` NFR-086. Content may include customer-identifiable examples and must be handled accordingly |

> **`SU-01` and `SU-09` are the two clauses that are always missing and always expensive.** A
> programme that changes supplier in month 20 with no export has paid twice for eighteen months
> of leverage and receives a different Bengali vocabulary for the second half of the build.

---

## 4. Segmentation

| # | Rule |
|---|---|
| **SG-01** | Segmentation rules are **declared, versioned and identical across every batch** (SRX or the tool's equivalent). Changing segmentation invalidates leverage |
| **SG-02** | **UI strings segment at the string**, not at the sentence. A two-sentence message is one segment because it is one key and must be reviewed as one unit |
| **SG-03** | **Prose content segments at the sentence**, using the Bengali দাঁড়ি `।` as a terminator alongside `.` `?` `!` |
| **SG-04** | An **ICU plural or select message is a single segment.** Splitting it destroys the structure and produces branches the translator cannot see |
| **SG-05** | Segments are stored **NFC-normalised** (`BN-006` `EN-02`). An NFD segment will never match |
| **SG-06** | **Placeholders are preserved as placeholders** in the segment, never resolved to an example value |

---

## 5. Term base structure

One entry per concept, not per word. Each entry carries:

| Field | Content |
|---|---|
| `concept_id` | Stable identifier |
| `en_term` | The `CG-004` approved English term |
| `bn_term` | The `BN-003` approved Bengali form |
| `tier` | `BN-002` §4 loanword tier |
| `part_of_speech` | Noun, verb, adjective |
| `definition` | From `CG-004` |
| `entity` | The `fix.*` model, where the term binds to one |
| `domain` | Organisation, party, service, commercial, finance, supply chain, quality, verb, concept |
| `status` | Approved · Deprecated · Proposed |
| `forbidden_en` | The banned English synonyms (`CG-004` §4) |
| `forbidden_bn` | **The specific wrong Bengali forms** (`BN-003` §4–§9 "Never" column) |
| `non_translatable` | True for `BN-004` Tier 1 |
| `surface_restriction` | Internal-only, customer-facing, Class A/B only |
| `source_ref` | `CG-004` §, `BN-003` § |
| `approved_on`, `approved_by` | Ratification record (`T-07`) |

| # | Rule |
|---|---|
| **TB-01** | **`forbidden_bn` is populated.** A term base that lists only the right answer does not prevent the wrong one; the CAT tool's QA check needs the wrong answers to flag them |
| **TB-02** | **`BN-003` is the source; the TB is the derivative.** The TB is regenerated from `BN-003`, never edited in place. Editing the TB directly creates a second glossary (`CP-01`) |
| **TB-03** | Master-data display values (~4,000) live **only** in the TB, not in `BN-003` (`BN-003` §16) |
| **TB-04** | The TB is delivered with **every** batch, and term-base QA is run before delivery, not after |
| **TB-05** | A **deprecated** term stays in the TB with `status: Deprecated` so that reintroduction is flagged (`BN-003` §15.3) |

---

## 6. Leverage

### 6.1 Match bands

| Band | Definition | Treatment | Typical rate basis |
|---|---|---|---|
| **Context / ICE** | 100% match **and** the same preceding and following segments | Locked; reviewed only if the surface changed | Lowest |
| **100%** | Exact source match, different context | Reviewed in context (`BN-018`) | Low |
| **95–99%** | Near match | Edited and reviewed | Medium |
| **85–94%** | Fuzzy | Edited and reviewed | Higher |
| **75–84%** | Weak fuzzy | Frequently faster to retranslate | Near full |
| **< 75%** | No match | New translation | Full |

| # | Rule |
|---|---|
| **LV-01** | **A 100% match is not automatically correct.** It is correct in the context it was approved in. `BN-018` in-context review still applies, because the same English on a button and in a confirmation dialog may need different Bengali (`BN-005` `CX-04`) |
| **LV-02** | **Context/ICE matches may be locked** and excluded from re-review **only where the surface is unchanged**, evidenced by the pinned release (`CG-006` §3) |
| **LV-03** | A match is **never accepted across a content-class boundary** without review. A Class D UI string reused in a Class B legal document is reviewed as new (`BN-002` `RD-C`) |
| **LV-04** | Leverage is **measured and reported per batch and per wave**, not estimated |
| **LV-05** | **Native-authored content is excluded from leverage targets** (`BN-001` `NA-04`) |

### 6.2 Expected leverage

Stated as an expectation with a basis, not a commitment (`RG-05`).

| Wave | Expected leverage | Basis |
|:--:|:--:|---|
| W1 | 5–15% | First substantial batch; leverage only from `MD` display values and cross-workspace repetition |
| W2 | 25–40% | `common.*` and `flow.*` already translated; `P01`/`P02` share heavily with `P03` |
| W3–W4 | 40–55% | Portal patterns established; notification and document sets repeat |
| W5–W7 | 50–65% | Mostly variation on established surfaces |
| W8–W9 | 60–75% | Optimisation and scale content |

> **These are expectations for planning, not contractual thresholds.** A wave that misses them is
> investigated — usually the cause is a segmentation change, an English rewrite, or a term change
> that invalidated segments (`TM-08`) — and the finding is more useful than the number.

---

## 7. Quality measurement

**Translation quality is measured with an error typology, not with an opinion.** The programme
adopts an **MQM-style** typology, scoped to the dimensions that matter here.

### 7.1 Dimensions

| Dimension | Examples in this programme |
|---|---|
| **Terminology** | A term not matching `BN-003`; a Tier 1 item transliterated (`BN-004`) |
| **Accuracy** | Omission, addition, mistranslation, a softened obligation (`CG-007` G4) |
| **Linguistic conventions** | Grammar, Bangla Academy spelling, punctuation, দাঁড়ি (`BN-002` §6) |
| **Style** | Wrong register, wrong address grade, unnatural word order (`BN-002` §2, §3, §5) |
| **Locale conventions** | Date, number, currency, address format (`BN-007`) |
| **Audience appropriateness** | Formal legal diction on a `P02` button; over-familiar tone in a warranty clause |
| **Design and markup** | Truncation, broken placeholder, lost `lang` marking, conjunct break (`BN-006`) |

### 7.2 Severity and scoring

| Severity | Definition | Weight |
|---|---|---:|
| **Critical** | Changes the meaning of an obligation, a price, a safety instruction or a legal position; or makes a statutory output non-compliant | **Batch fails. Not scored — rejected** |
| **Major** | Would mislead or block a user; wrong term; wrong register throughout | **5** |
| **Minor** | Noticeable but does not mislead; inconsistent but comprehensible | **1** |

| # | Rule |
|---|---|
| **QM-01** | Score is computed per 1,000 words: `(5 × majors + 1 × minors) ÷ words × 1000` |
| **QM-02** | **Any critical error fails the batch**, regardless of score. There is no offsetting |
| **QM-03** | **Acceptance threshold: ≤ 10 for Class C and D; ≤ 5 for Class A and B; 0 criticals in all classes** |
| **QM-04** | Sampling is **20% for a new supplier or a new linguist, 10% thereafter, 100% for Class A and B** |
| **QM-05** | **`CG-004` §9 sets a terminology defect-rate target below 2%**; this file's Terminology dimension is how that is measured for Bengali |
| **QM-06** | Scores are recorded per linguist and per batch, and trended. A rising score is a capacity or briefing problem before it is a quality problem |
| **QM-07** | **Quality measurement does not replace G4 in-context review** (`BN-018`). A batch can score 3 and still fail in context, because truncation and slot mismatch are not visible in a bilingual file |

---

## 8. Update cycle

**The single most-broken rule in translation memory management: writing to the TM before the
translation is approved.**

| # | Rule |
|---|---|
| **TM-06** | **A segment enters the TM only after G4 sign-off** (`CG-007` §3.4). A delivered-but-unreviewed segment in the TM propagates an unreviewed answer to every future batch |
| **TM-07** | Segments are written with metadata: content class, surface, wave, approval date, approver, and the `BN-003` version in force |
| **TM-08** | **A `BN-003` term change marks every containing segment for re-review**, not silent reuse (`BN-003` §15.2). This is the main cause of leverage dropping between waves and it is correct behaviour |
| **TM-09** | **A superseded segment is retired, not deleted.** The TM keeps history (`CP-10`) |
| **TM-10** | The TM is **cleaned at every wave boundary** — duplicates merged, orphans removed, penalties reviewed |
| **TM-11** | **Penalties are applied** for segments from a different content class, a different surface type, or an older `BN-003` version, so that the match band reflects real reusability |
| **TM-12** | **The corporate-website Bengali content is a separate memory** and is attached as a **reference** TM with a penalty, never merged. The two content sets are deliberately separate (Master Index §11) and their registers differ (`BN-003` §11 D-1, D-2) |
| **TM-13** | **Machine-translated segments never enter the TM**, in any circumstance, including from a permitted draft under `CG-010` §6.2 |

---

## 9. Access and security

| Role | TM | TB | Write |
|---|:--:|:--:|:--:|
| Localisation Lead | Full | Full | **Yes** |
| Translator (supplier) | Read + propose | Read | Proposals only |
| Linguistic reviewer | Read + propose | Read | Proposals only |
| Content authors | Read | Read | No |
| Developers | No | **Read** — the TB is how a developer checks a term | No |
| Enterprise Architecture | Read | **Full** on `BN-003`-derived entries | Via `BN-003` |

| # | Rule |
|---|---|
| **AC-01** | **Only the Localisation Lead writes to the TM**, and only on G4 evidence (`TM-06`) |
| **AC-02** | Supplier access is **per-project and time-boxed**, revoked at contract end (`SU-09`) |
| **AC-03** | Content sent for translation is **de-identified where it contains real customer data**. Test data comes from `TS-002`, which exists for this reason |
| **AC-04** | Class A and B content sent to a supplier is flagged and is subject to `LG-006` supplier terms |
| **AC-05** | The TM is backed up with the content repository and is in scope for the same retention schedule (`LG-009`) |

---

## 10. Metrics

Reported at every wave boundary into `CG-014`.

| Metric | Definition | Why |
|---|---|---|
| TM size | Approved segments | The asset's growth |
| Leverage rate | Weighted match value / total words | Cost avoidance |
| **Cost per new word, trended** | Spend ÷ no-match words | The number `AF-09` needs |
| MQM score by class | §7.2 | Quality trend |
| Critical error count | Absolute | **Target zero** |
| G4 turnaround | Working days after English approval | Against the 5-day service level (`CG-007` §6) |
| G4 rejection rate | Batches failing in-context review | Briefing quality, not linguist quality |
| Query volume per 1,000 words | Translator queries | **A rising rate means the English is unclear** (`BN-002` `TX-03`) |
| Term base coverage | Terms in the TB ÷ terms in use | Gaps before they become defects |
| Linguist concentration | Share of volume by one linguist | `CG-013` `CR-04` |

> **Query volume is the most useful metric in this table and the least used.** A translator asking
> many questions is not a poor translator; it is a signal that the English source is ambiguous,
> and the cheapest place to fix that is in the English.

---

## 11. Open decisions

| # | Decision | Owner | Needed by | Blocks |
|---|---|---|---|---|
| 1 | **Translation sourcing model** — in-house, agency, or both. Inherited from `CG-010` §12 item 5 and `BN-001` §12 item 6 | Localisation Lead with Procurement | **Before W1** | Every clause in §3; the capacity plan; `AF-09` |
| 2 | **Which CAT/TMS platform**, and does 1000FiX hold the tenancy or the supplier? (`TM-03`) | Localisation Lead with Platform Engineering and Procurement | Before W1 | §9 access model, `SU-02` |
| 3 | Is the TM in scope for the **`05-06` NFR-086 residency** requirement, given it may contain customer-identifiable examples? | **DPO with Legal Counsel** | Before the first batch leaves the company | `SU-05`, `AC-03`, `LG-012` |
| 4 | Are the MQM thresholds in `QM-03` contractually binding on the supplier, or internal acceptance criteria? | Procurement with Localisation Lead | Before contract | `SU-06`, §7 |
| 5 | How is **reviewer independence** guaranteed where the market of qualified Bengali ERP linguists is small? | Localisation Lead with Procurement | Before W1 | `CO-05`, `SU-06`, `CG-013` `CR-04` |

---

## 12. Dependencies

| Depends on | Why |
|---|---|
| `BN-002` | The style guide package supplied with every batch |
| `BN-003` | The source the TB is generated from (`TB-02`) |
| `BN-004` | The DNT entries (`TM` non-translatable flags) |
| `BN-005` §5 | Context notes that must travel with the segment |
| `BN-018` | The G4 evidence `TM-06` requires |
| `CG-006` | Versioning and retention of the assets |
| `CG-007` §3.4, §6 | The G4 gate and its service level |
| `LG-006`, `LG-009`, `05-06` NFR-086 | Supplier terms, retention and residency |
| `TS-002` | De-identified test data for translation samples (`AC-03`) |

---

## 13. Related documents

| Document | Relationship |
|---|---|
| [`BN-002_Bengali_Translation_Standard.md`](BN-002_Bengali_Translation_Standard.md) | The style guide asset; §9 translator inputs |
| [`BN-003_Bilingual_Terminology_Glossary.md`](BN-003_Bilingual_Terminology_Glossary.md) | The TB source |
| [`BN-004_Do_Not_Translate_and_Transliteration_Register.md`](BN-004_Do_Not_Translate_and_Transliteration_Register.md) | The DNT asset |
| [`BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md`](BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md) | The gate `TM-06` waits for |
| [`../00_Content_Governance_and_Standards/CG-013_Content_Risk_and_Legal_Escalation_Rules.md`](../00_Content_Governance_and_Standards/CG-013_Content_Risk_and_Legal_Escalation_Rules.md) | `CR-04` translation capacity risk |
| [`../00_Content_Governance_and_Standards/CG-014_Content_Metrics_and_Effectiveness_Measurement.md`](../00_Content_Governance_and_Standards/CG-014_Content_Metrics_and_Effectiveness_Measurement.md) | Where §10 reports |

---

## 14. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-17 | Initial issue. Seven localisation assets defined with open interchange standards (TMX 1.4b, TBX ISO 30042:2019, XLIFF); ten supplier clauses including ownership, export, no-MT-training and exit; six segmentation rules including the ICU-message-as-one-segment rule; fifteen-field term base with the forbidden-Bengali field; six match bands with the 100%-is-not-automatically-correct rule; expected leverage by wave stated as expectation with basis; MQM-style typology with severity weights, thresholds and the critical-fails-the-batch rule; thirteen TM update rules including G4-before-write and the website-TM-as-reference-only rule; access model; ten metrics; five open decisions | Programme Content Lead (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] All localisation assets enumerated with an owner and an open interchange format
- [x] **Ownership, export and exit stated as contract requirements**, because that is where they must live
- [x] Segmentation rules stated, including the ICU-message rule that protects plural structure
- [x] Term base structure includes the **forbidden Bengali forms**, without which tool QA cannot flag anything
- [x] Leverage bands defined with the rule that a 100% match still needs in-context review
- [x] Expected leverage stated as an expectation with a basis, per `RG-05`
- [x] Quality measured with a typology and a threshold, with criticals failing outright
- [x] The G4-before-TM-write rule stated as the central discipline
- [x] The corporate-website memory treated as reference-only, consistent with Master Index §11
- [x] Metrics defined including query volume as a signal about the **English**
- [x] All internal links resolve
- [x] Bengali counterpart — n/a; internal standard, English-only by `CG-010` §3.2
- [ ] **Sourcing model decided** — outstanding; §11 item 1, `W1` blocker
- [ ] **Platform and tenancy decided** — outstanding; §11 item 2
- [ ] **TM residency position confirmed by DPO** — outstanding; §11 item 3, blocks the first external batch
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
