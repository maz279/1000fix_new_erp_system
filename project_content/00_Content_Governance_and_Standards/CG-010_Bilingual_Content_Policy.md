---
id: CG-010
title: Bilingual Content Policy
project: 1000FiX ERP System v2.0
content_type: Policy
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Localisation Lead
author: Localisation Lead with Programme Content Lead
reviewers: [Content Design Lead, Enterprise Architecture, Legal & Compliance, Brand]
approver: ERP Steering Committee
purpose: >
  Decides, once and in advance, which of the 452 content files must exist in Bengali, which are
  English-only, which language is the source of truth for each type, and where machine
  translation is prohibited. 266 files need Bengali. Deciding this per file, late, is how
  bilingual programmes fail — the decision arrives after the schedule, the budget and the
  translation capacity have all been set on the wrong assumption.
traces_to: [04-00 PS-03, 05-06 NFR-016, 05-06 NFR-073, 05-06 NFR-074, 05-06 §9, P02 non-negotiable 3, P01 design requirements, CP-05, CM-R6]
priority: P0
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §3 PS-03 — Bengali and English throughout, Bengali default on customer and field surfaces
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P02 non-negotiable requirement 3 — Bengali user interface, complete, including error messages
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P01 design requirements — professionally translated, not machine-translated
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §5 NFR-016, NFR-073, NFR-074 and §9 Localisation Standards
    verified: 2026-08-15
  - source: 1000_fix_corporate_website project_content BN-001 Bengali Translation Guidelines v1.0 — register selection for marketing content
    verified: 2026-08-15
supersedes: none
review_due: 2026-11-15
---

# CG-010 — Bilingual Content Policy

> **Three contractual commitments drive this policy.** None is negotiable and all three are
> already in approved specifications:
>
> | Commitment | Source |
> |---|---|
> | Bengali and English throughout, with **Bengali default** on customer and field surfaces | `04-00` PS-03 |
> | The technician application's Bengali interface must be **complete — including error messages** | `04-00` §P02 non-negotiable #3 |
> | Customer content must be **professionally translated, explicitly not machine-translated** | `04-00` §P01 design requirements |
>
> `05-06` NFR-016 restates the first as a `P0` non-functional requirement: full Bengali and
> English support in interfaces, notifications, reports **and data entry**.

---

## 1. The decision this file makes

Bilingualism is not a property a file acquires late. It changes:

| What it changes | How |
|---|---|
| **Authoring** | English must be written to be translatable — no concatenation, no idiom, no embedded formatting (`CG-003` S-05, S-06) |
| **Schedule** | The wave gate is set by the Bengali sign-off, not the English one (`CG-007` §5) |
| **Cost** | Roughly 60% of the `BN` category's 180–280 person-day estimate is volume-driven by decisions made here |
| **Design** | Bengali runs 20–40% longer than English; layouts must accommodate it from the first wireframe (`VB-007`, `BN-006`) |
| **Testing** | Every bilingual surface needs a bilingual test pass (`TS-016`, `CG-008` TS-d) |
| **Approval** | The pair moves together; neither publishes alone (`CM-R6`, `LC-08`) |

**Deciding per file, at authoring time, means all six decisions are made after they can be
acted on.** This policy makes them all at Wave 0.

---

## 2. Principles

| # | Principle |
|---|---|
| **BP-01** | **Bengali is a first-class deliverable, not a translation afterthought** (`CP-05`). A bilingual file is not complete until both languages are signed off |
| **BP-02** | **Bengali is the default on customer and field surfaces** (`PS-03`). English is the toggle, not the baseline |
| **BP-03** | **English is the source of truth for structure; Bengali is the source of truth for Bengali wording** once linguistically signed off (`BN-018`) |
| **BP-04** | **Machine translation is prohibited** on customer- and field-facing content. Narrow exceptions in §6 |
| **BP-05** | **Partial bilingualism is worse than none.** A screen that is 80% Bengali teaches the user the product is not for them. Coverage is per surface, not per string |
| **BP-06** | **Some content is deliberately English-only.** Declaring it is a decision, not a gap |
| **BP-07** | **Translate meaning, not words.** Where a literal translation would mislead, the Bengali is written to convey the obligation, and the divergence is recorded |
| **BP-08** | **Statutory and technical identifiers are never translated** (`BN-004`) |
| **BP-09** | **The pair versions together.** Same version number, same approval state (`LC-08`) |
| **BP-10** | **In-context review is mandatory.** Translation reviewed as a string list passes review and fails in production (`CG-007` G4, `BN-018`) |

---

## 3. The coverage decision

### 3.1 Summary

| | Files | Share |
|---|---:|---:|
| **Bilingual — English and Bengali both required** | **266** | 59% |
| English-only | 186 | 41% |
| **Total** | **452** | 100% |

### 3.2 Coverage by category

| Category | Total | Bilingual | English-only | Rationale for the split |
|---|---:|---:|---:|---|
| `CG` Content Governance | 14 | **0** | 14 | Internal governance read by the content workstream, which works in English. Translating it would consume capacity needed for user-facing content |
| `VB` Voice & brand | 10 | **5** | 5 | `VB-002`, `VB-007`, `VB-008`, `VB-009`, `VB-010` carry Bengali examples, labels and naming. The rest are internal design standards |
| `MD` Master data | 48 | **22** | 26 | Any dataset whose values are displayed to a user needs Bengali name columns — branches, geography, roles, catalogue, service types, device models, fault codes, resolution codes, reason codes, status labels, SLA definitions, warranty types, contract templates, loyalty tiers, calendars, party standards, segments, parts, price lists, tax terms, payroll elements, e-waste categories. Structural datasets (locations, dimensions, sequences, FX, asset classes) do not |
| `UI` UI copy | 42 | **42** | 0 | Every interface surface. `PS-03` admits no exception |
| `NT` Notifications | 26 | **20** | 6 | Every message that reaches a **Bengali-reading** human. `NT-001`, `NT-003`, `NT-021`, `NT-026` are governance and internal alerting; `NT-011` vendor and `NT-013` brand-partner email follow the §3.3 audience rule and are English-only |
| `DT` Documents & print | 44 | **34** | 10 | Everything given to a customer, employee, or presented to a regulator. Vendor-, brand- and B2B-facing procurement documents remain English (`DT-021`–`DT-025`, `DT-029`, `DT-033`, `DT-039`, `DT-040`) plus the `DT-001` standard |
| `SP` Process & SOP | 34 | **28** | 6 | SOPs are executed by branch and field staff across 51+ locations. `SP-001`–`SP-006` are architecture and matrices for head office |
| `KB` Knowledge | 16 | **13** | 3 | Technicians read knowledge in the field, in Bengali. `KB-001`, `KB-002`, `KB-015` are governance |
| `TR` Training | 24 | **20** | 4 | All course packs. `TR-001`–`TR-004` are the framework |
| `HC` Help centre | 20 | **18** | 2 | All help sets and AI content. `HC-001`, `HC-002` are IA and template |
| `LG` Legal & compliance | 24 | **16** | 8 | Consumer- and employee-facing terms, privacy, warranty, refund, data. Vendor, seller, brand and internal policy sets remain English — those counterparties contract in English |
| `BN` Localisation | 18 | **10** | 8 | The string bundles and packs (`BN-009`–`BN-017`) **are** Bengali artefacts; `BN-003` is inherently bilingual. The standards and plans are English |
| `DM` Data migration | 14 | **0** | 14 | Technical mapping worked by the migration team |
| `TS` Test & acceptance | 18 | **7** | 11 | Scripts executed by Bengali-speaking business users, plus the bilingual and accessibility packs |
| `RP` Reporting & KPI | 16 | **5** | 11 | Dashboard labels, report catalogue, chart standards, league table and KPI names reach branch managers. Semantic layer and governance do not |
| `AP` Integration & developer | 12 | **0** | 12 | Developer audience; the industry works in English and every counterparty integration team does |
| `CM` Change & comms | 18 | **12** | 6 | Anything reaching branch, field or customer audiences. Executive and PMO material is English |
| `OP` Operations & runbooks | 16 | **4** | 12 | `OP-003` macros, `OP-004` incident templates, `OP-005` status page, `OP-014` manual fallback — all read under pressure by branch staff. Runbooks are for engineers |
| `EO` Ecosystem onboarding | 14 | **8** | 6 | Seller, rider and corporate-user-facing kits. Brand partner and supplier material is English |
| `MM` Multimedia specs | 12 | **0** | 12 | Specifications for suppliers, who work in English. The **assets they produce** are bilingual; the briefs are not |
| `RF` Reference & registers | 12 | **2** | 10 | `RF-001` glossary and `RF-009` sample pack. Registers are internal |
| **Total** | **452** | **266** | **186** | |

### 3.3 The rule behind the split

> **If a person outside the programme's English-working core will read it to do their job or
> make a decision, it is bilingual.**

| Audience | Bilingual? |
|---|:--:|
| Customers (250,000+/month) | **Yes** |
| Field technicians (200–400) | **Yes** |
| Branch and front-desk staff (150–250 agents, 51+ branches) | **Yes** |
| Riders and logistics staff (50–200) | **Yes** |
| Marketplace sellers (500–2,000) | **Yes** |
| Employees generally, for HR and payroll content | **Yes** |
| Corporate client users (500–2,000) | **Partly** — portal UI yes; contractual and technical documents English |
| Brand partners (17+, international) | No |
| Vendors and suppliers | No |
| Developers and integration partners | No |
| Executives, PMO, architects, the content workstream | No |

---

## 4. Source of truth

| Content type | Authored in | Source of truth for meaning | Source of truth for Bengali wording |
|---|---|---|---|
| UI copy | English | English | Bengali after G4 sign-off |
| Notifications | English | English | Bengali after G4 sign-off |
| Documents and print | English | English | Bengali after G4 sign-off |
| Legal and statutory | English | **English, always** | English — the Bengali is a translation and says so |
| Master data name columns | English + Bengali together | Both, per column | Bengali column |
| Knowledge articles | **Bengali where the author is a Bengali-speaking technician** | Whichever was authored first | — |
| Field technician training | **Bengali natively** (`BN-016`) | Bengali | Bengali |
| Contact centre and IVR scripts | Bengali natively | Bengali | Bengali |
| Chatbot intents and utterances | Both natively | Both | Both |
| Everything else bilingual | English | English | Bengali after G4 sign-off |

### 4.1 The legal exception — `BP-03` does not apply to Class B

**For legal and statutory content, English governs in a dispute.** The Bengali version is
provided so the counterparty understands the obligation; it is not an independent instrument.
Every bilingual Class A or B document carries a precedence clause stating this, drafted once in
`LG-001` and reproduced in each document.

> This is a legal decision, not a linguistic one. It must be confirmed by Legal Counsel before
> the first bilingual legal document is issued, and logged in `RF-006`. Where Bangladesh law
> requires a Bengali instrument to govern, that requirement overrides this position and the
> affected documents are re-approved.

### 4.2 Bengali-native content

Three content types are **authored in Bengali first**, not translated:

| Type | Why | File |
|---|---|---|
| Field technician training | 200–400 technicians with mixed English literacy. Translated training teaches translated concepts; native training teaches the job | `TR-009`, `BN-016` |
| Contact centre and IVR scripts | Spoken Bengali has a different rhythm from written translated Bengali. A translated script sounds wrong on a call | `SP-034`, `NT-019`, `BN-017` |
| Chatbot utterances | Users type what they actually say. Translated utterances train the model on Bengali nobody uses | `HC-017` |

For these, the **English version is the translation** and is produced for review and governance
purposes.

---

## 5. Coverage is per surface, not per string

`BP-05`. A surface is bilingual only when **100% of its user-visible strings** are, including:

| Often missed | Why it matters |
|---|---|
| Error and validation messages | `P02` non-negotiable #3 names these explicitly |
| Empty states and zero-data screens | The first screen every user sees at go-live |
| Loading, progress and timeout copy | The screens users see when things go wrong |
| Offline and sync-conflict copy | `PS-08` surfaces operate offline for 24 hours |
| Confirmation and destructive-action dialogs | The highest-consequence moment in any flow |
| Form placeholders and help text | |
| Date pickers, dropdowns and system-generated values | Frequently inherited from a library in English |
| Accessibility text — alt, ARIA labels, screen-reader-only | `CG-011` §8 |
| Notification subjects and preview text | |
| Printed document field labels | |
| PDF metadata and file names presented to users | |
| Third-party component strings | Payment widgets, map controls, date pickers |

**Sign-off is per surface.** A surface with any English string remaining fails G4.

---

## 6. Machine translation

### 6.1 Prohibited

`04-00` §P01 states customer content must be professionally translated, **explicitly not
machine-translated**. This policy extends the prohibition to every Class A, B, C and D bilingual
file — that is, all 266.

| # | Rule |
|---|---|
| **MT-01** | Machine translation may **never** be published on any bilingual surface |
| **MT-02** | Machine translation may **never** be the basis of a Class A or B file, in any form |
| **MT-03** | A translation produced by machine and then edited is machine translation and is prohibited on customer- and field-facing content |
| **MT-04** | Violating MT-01 is a `CG-008` blocking item (`B-09`) and cannot be waived (`WV-03`) |

### 6.2 Permitted, narrowly

| Use | Permitted | Conditions |
|---|:--:|---|
| Understanding an inbound Bengali message internally | Yes | Never republished |
| Producing a first draft for a **professional translator** to work from | Yes | The translator's output is the deliverable; the draft is discarded. Must be declared |
| Translating internal English-only governance for a reader's convenience | Yes | Marked as an unofficial machine translation |
| Real-time assistance inside the AI assistant (`M32`) | **Conditional** | Only with an explicit AI disclosure (`HC-019`) and only where the assistant does not commit the company to a price, promise or legal position |
| Any published content | **No** | — |

### 6.3 The exception decision

Any exception requires **both** the Localisation Lead and the Programme Content Lead
(`CG-002` §7.1), is time-boxed, and is logged in `RF-006`. Neither may grant it alone.

---

## 7. Register and dialect

**The register question is open and must be closed before any `BN` bundle is produced.**

| Consideration | Position |
|---|---|
| The corporate website selected **modern colloquial Bengali (চলিত ভাষা)** for marketing content (`BN-001`) | Established precedent for consumer-facing tone |
| ERP customer surfaces address the same audience | Argues for the same register |
| ERP statutory and legal documents are read alongside government forms in formal Bengali | Argues for a more formal register in Class A and B |
| ERP field and branch surfaces are operational instructions | Argues for plain, direct Bengali, closer to colloquial |
| Mixing registers within one product is itself a defect | Argues for a single decision with a narrow, declared exception |

**Proposed position, for `BN-002` to confirm:** modern standard Bengali (চলিত) across all
surfaces, with a **declared formal register for Class A and B legal and statutory documents
only**, where the surrounding regulatory context sets the expectation.

| # | Rule |
|---|---|
| **RD-01** | The register decision is made once in `BN-002`, applies to all surfaces, and is logged in `RF-006` |
| **RD-02** | সাধু ভাষা (classical Bengali) is not used anywhere in the ERP |
| **RD-03** | Regional dialect is not used. Standard Bengali serves all eight divisions |
| **RD-04** | Code-mixing — English words in Bengali sentences — follows `BN-002`, which is more restrictive for statutory content than for UI |
| **RD-05** | Transliteration of technical terms follows `BN-003`, informed by the website glossary where the term is already established with customers |

---

## 8. Bengali-specific constraints that change authoring

These are not translation problems; they are **English authoring** problems that only surface in
Bengali. Authors must know them before writing.

| # | Constraint | Consequence for the English author |
|---|---|---|
| **BC-01** | **Text expansion of 20–40%** | Do not write to a tight character limit and assume Bengali fits. Declare the budget for the longer language |
| **BC-02** | **No letter case** | Never use capitalisation to convey meaning. `CG-003` sentence case already handles this |
| **BC-03** | **Different word order** | Never concatenate strings. "You have {n} items" cannot be assembled in Bengali order from English fragments (`BN-005`, `CG-003` S-05) |
| **BC-04** | **Conjunct rendering breaks at small sizes** | Do not specify type below the `BN-006` minimum. Affects `P02` on mid-range Android, the exact device class technicians use |
| **BC-05** | **SMS is UCS-2** | Bengali SMS segments at **70 characters**, not 160. A 150-character English template is one segment; its Bengali equivalent may be three (`NT-004`, `BN-014`) |
| **BC-06** | **Numerals may be Bengali or Arabic** | The policy is set in `BN-007`; do not decide per string |
| **BC-07** | **Lakh and crore grouping** | 12,34,567 in the Bengali locale (`05-06` §9). Never format numbers in content; let the locale do it |
| **BC-08** | **Collation differs** | Sorting and search use ICU `bn-BD` (`05-06` §9). Do not assume alphabetical order transfers |
| **BC-09** | **Screen reader support is uneven** | Bengali screen-reader quality varies by engine. `CG-011` §8 sets what is testable and what is a known limitation |
| **BC-10** | **Phonetic input is the norm** | Users type Bengali phonetically (`NFR-074`). Search and matching content must accommodate spelling variation |

---

## 9. Capacity and schedule consequence

| Item | Position |
|---|---|
| Bilingual files | 266 |
| `BN` category estimate | 180–280 person-days (Master Index §7) |
| Translation is **volume-driven** | It scales with `UI`, `NT` and `DT` output, not with its own file count |
| G4 service level | 5 working days **after** English approval (`CG-007` §3.4) |
| Linguistic reviewers must be independent of translators | `CO-05` — at least two Bengali resources are required, not one |
| Escalation trigger | Translation capacity is escalated at **wave gate minus 6 weeks** (`CG-002` §7) |

**The scheduling consequence, stated plainly:** for any bilingual `P0` content, the wave gate is
set by the Bengali sign-off date. Plan backwards from the gate by translation time plus the G4
service level plus rework. A wave plan that shows English content completing at the gate has
already missed it.

---

## 10. Verification

| Check | Where | When |
|---|---|---|
| `bilingual:` front matter matches this policy | Automated (`CG-008` §6) | Every commit |
| A `_BN` counterpart exists for every `bilingual: yes` file | Automated | Every commit |
| Both files carry the same version | Automated | Every commit |
| Surface coverage is 100% — no residual English strings | G4 in-context review (`BN-018`) | Per surface |
| No machine translation published | G4 review + translator attestation | Per file |
| Truncation and layout hold at target sizes | G4 in-context review | Per surface |
| Terminology matches `BN-003` | Automated term scan + G4 | Every commit and per file |
| Do-not-translate items untranslated | Automated scan against `BN-004` | Every commit |
| Bengali rendering on target printers | `DT` files, physical test | Before each `DT` release |
| Bengali rendering on mid-range Android | `P02`, `P09` surfaces, device test | Before each mobile release |
| Coverage count still reconciles to 266 | Wave audit | Every wave boundary |

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`CG-003_ERP_Product_Content_Style_Guide.md`](CG-003_ERP_Product_Content_Style_Guide.md) | English authoring rules that make translation possible |
| [`CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) | Terms whose Bengali equivalents `BN-003` binds |
| [`CG-007_Review_Approval_and_Signoff_Workflow.md`](CG-007_Review_Approval_and_Signoff_Workflow.md) | Gate G4 and the bilingual pair rule |
| [`CG-008_Content_Definition_of_Done_and_QA_Checklist.md`](CG-008_Content_Definition_of_Done_and_QA_Checklist.md) | U-42 to U-48 |
| [`CG-011_Accessibility_Content_Standard.md`](CG-011_Accessibility_Content_Standard.md) | Bengali screen-reader considerations |
| `BN-001` Localisation Strategy & Language Coverage Matrix | Operationalises this policy per surface |
| `BN-002` Bengali Translation Standard | Closes the register question in §7 |
| `BN-003` Bilingual Terminology Glossary | The Bengali binding for `CG-004` |
| `BN-004` Do-Not-Translate and Transliteration Register | `BP-08` |
| `BN-005` i18n Key, Placeholder and Pluralisation Rules | `BC-03` |
| `BN-006` Bengali Typography, Font and Numeral Standard | `BC-04`, `BC-06` |
| `BN-007` Date, Time, Number, Currency and Address Formats | `BC-07` |
| `BN-018` Localisation QA and Linguistic Sign-off Checklist | The mechanics of `BP-10` |
| `05-06` §9 Localisation Standards | The technical standards this policy sits on |

---

## 12. Open decisions

| # | Decision | Owner | Needed by | Blocks |
|---|---|---|---|---|
| 1 | Bengali register — single standard register, or formal for Class A/B? (§7) | Localisation Lead, ratified by Content Lead | Before W1 | All `BN` bundles |
| 2 | Does English govern in a dispute for bilingual legal documents? (§4.1) | Legal Counsel | Before the first bilingual legal document | `LG-002`, `LG-013`, `LG-015` |
| 3 | Bengali or Arabic numerals as the default in the Bengali locale (`BC-06`) | Localisation Lead with Design | Before W1 | `BN-006`, `BN-007`, every `UI` pack |
| 4 | Corporate portal (`P04`) — is the UI bilingual while its documents stay English? | Account Management with Localisation | Before W4 | `UI-014`, `BN-012` |
| 5 | Translation sourcing — in-house team, agency, or both, and how independence of reviewers is guaranteed | Localisation Lead with Procurement | Before W1 | Capacity plan, `AF-09` |

---

## 13. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Coverage decided for all 21 categories reconciling to 266 bilingual files, source-of-truth rules with the legal exception, Bengali-native content types, machine-translation prohibition with narrow exceptions, ten Bengali-specific authoring constraints, five open decisions | Steering Committee (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] Coverage decided for every category, reconciling to 266 of 452
- [x] The rule behind the split is stated so future files can be classified without re-deciding
- [x] Source of truth stated per content type, with the legal exception flagged for counsel
- [x] Machine-translation prohibition traced to `04-00` §P01 and made a blocking item
- [x] Bengali-specific constraints stated as **English authoring** rules, where they can be acted on
- [x] Schedule consequence stated plainly rather than implied
- [x] All internal links resolve
- [x] Bengali counterpart — n/a; this is internal governance (`CG` is English-only by §3.2)
- [ ] Named approver recorded — **pending Steering Committee**
- [x] Registered in the Content Master Index
- [x] Open decisions listed with owners and blocking consequences

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
