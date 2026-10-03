---
id: BN-001
title: Localisation Strategy and Language Coverage Matrix
project: 1000FiX ERP System v2.0
content_type: Strategy
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Localisation Lead
author: Localisation with Programme Content Lead and Platform Engineering
reviewers: [Programme Content Lead, Content Design Lead, Enterprise Architecture, Platform Engineering, all portal owners, Legal & Compliance]
approver: Programme Content Lead
content_class: E
purpose: >
  Turns the CG-010 category-level bilingual decision into a per-surface, per-content-type
  operating matrix: which language is the default on each of the twelve portals and every
  print, message and voice surface, how a user's language is resolved at runtime, which
  content is authored natively in Bengali, and which BN file owns each body of Bengali
  wording. Without it the 267 bilingual files are translated by whoever reaches them first,
  the shared common.* namespace is translated once per portal, and partial bilingualism —
  which PS-03 explicitly does not permit — arrives surface by surface.
traces_to: [04-00 PS-03, 04-00 §P01, 04-00 §P02, 05-06 NFR-016, 05-06 NFR-074, 05-06 §9, M65, CG-010, CG-004, UI-001, BN-002, BN-003, BN-018]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §3 PS-03 — "Bengali and English throughout, with Bengali default on customer and field surfaces", applies to All
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P01 Design Requirements — "Bengali-first, with English toggle; all content professionally translated, not machine-translated"
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P02 Non-Negotiable Requirements #3 — "Bengali user interface, complete — including error messages"
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §5 NFR-016 (P0) — "Full Bengali and English support in interfaces, notifications, reports and data entry"; NFR-074 (P1) — Bengali input including phonetic typing and voice-to-text on mobile
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §9 Localisation Standards — bn-BD primary for field and customer, en secondary, UTF-8, ICU bn-BD collation, translation completeness 100% of user-facing strings before any module is accepted
    verified: 2026-08-17
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-010 §3.2 — category-level bilingual split reconciling to 266 of 452 files
    verified: 2026-08-17
    class: P1
  - source: Bangla Bhasha Prachalan Ain, 1987 (Act No. 2 of 1987), §3 — records, correspondence and proceedings in courts, government and semi-government offices and autonomous institutions must be in Bengali
    verified: 2026-08-17
    class: P2
supersedes: none
review_due: 2026-11-17
---

# BN-001 — Localisation Strategy and Language Coverage Matrix

> **`CG-010` decided *how many* files are bilingual. This file decides *what the user
> actually sees*.**
>
> Those are different problems. A category can be 100% bilingual on paper and still present
> a technician with an English toast message, because the toast lives in `common.*`, which
> belongs to no portal and therefore to no bundle. `PS-03` is a **surface** commitment, and
> surfaces are assembled from namespaces owned by different files. This matrix is where the
> assembly is made explicit.

---

## 1. Purpose

| | |
|---|---|
| **What this governs** | Default language and toggle behaviour per surface; language resolution at runtime; which `BN` file owns which body of Bengali wording; data-entry language; wave coverage gates |
| **What it does not govern** | Which categories are bilingual (`CG-010` §3); how Bengali is written (`BN-002`); which term is used (`BN-003`); typography (`BN-006`); formats (`BN-007`); sign-off (`BN-018`) |
| **What breaks without it** | Shared strings translated once per portal and divergently; the `common.*` namespace unowned; surfaces that are 90% Bengali, which `BP-05` classifies as worse than none; no wave gate that can be failed |

**Relationship to `CG-010`.** `CG-010` is the **policy** and is owned by the Localisation Lead
jointly with the Programme Content Lead; it decides coverage at category level and is ratified
by the Steering Committee. `BN-001` is the **operating matrix** and is owned by the Localisation
Lead alone; it decides coverage at surface level. Where they disagree, `CG-010` governs and this
file is corrected (`CP-01`).

---

## 2. The commitments this matrix must satisfy

| # | Commitment | Source | What it forces |
|---|---|---|---|
| **C-1** | Bengali and English throughout, **Bengali default** on customer and field surfaces | `04-00` PS-03 | A declared default per surface, not per user |
| **C-2** | `P01` is **Bengali-first with an English toggle**, professionally translated | `04-00` §P01 Design Requirements | The toggle is the exception path; the Bengali is the build |
| **C-3** | `P02`'s Bengali interface is **complete, including error messages** | `04-00` §P02 non-negotiable #3 | `common.error.*` must be Bengali before `P02` ships, and `common.*` is not owned by `BN-010` |
| **C-4** | Full Bengali and English support in interfaces, notifications, reports **and data entry** | `05-06` NFR-016 (`P0`) | Bengali is an **input** requirement, not only an output one — §7 |
| **C-5** | Bengali input including phonetic typing and voice-to-text on mobile | `05-06` NFR-074 (`P1`) | Search and matching must tolerate phonetic spelling variation (`BN-003` §9) |
| **C-6** | **100% of user-facing strings** translated before any module is accepted | `05-06` §9 | The wave gate in §9 is an acceptance gate, not a quality aspiration |
| **C-7** | Records and correspondence filed with government, semi-government and autonomous bodies, and proceedings in court, must be in Bengali | Bangla Bhasha Prachalan Ain 1987 §3 | Statutory and regulator-facing output is a **legal** Bengali obligation, not a usability one — §6.4 |

> **C-7 is new to this programme's content set and is not yet reflected in Category 10.**
> `CG-010` §3.2 places legal content on an audience test and marks vendor, seller, brand and
> internal policy sets English-only. That test is correct for *counterparty* documents. It does
> not reach documents the company **files with a public body**, where the 1987 Act applies
> irrespective of who reads them. Raised as an open decision in §12 for Legal Counsel.

---

## 3. Surface coverage matrix

**Reading the columns.** *Default* is what an unauthenticated or first-time user sees.
*Toggle* is whether the user may change it and where the choice persists. *Completeness* is the
share of user-visible strings that must exist in Bengali before the surface may be accepted.

### 3.1 The twelve portals

| Surface | Audience | Default | Toggle | BN completeness required | English completeness required | Owning bundle |
|---|---|---|:--:|:--:|:--:|---|
| **P01** Customer portal & app | 250,000+/month consumers | **Bengali** | Yes — persisted to `fix.party.preferred_language` | **100%** | 100% | `BN-009` |
| **P02** Technician application | 200–400 field & workshop | **Bengali** | Yes — device-local only | **100% — including every error and offline message** | 100% | `BN-010` |
| **P03** Admin & operations portal | 150–250 agents, 51+ branches, back office | **Bengali** | Yes — persisted to the user record | **100%** | 100% | `BN-011` |
| **P04** Corporate B2B portal | 500–2,000 corporate users | **English** | Yes | **100%** | 100% | `BN-012` |
| **P05** Vendor & supplier portal | Suppliers | English | Yes | **100% of UI**; documents English (`CG-010` §3.2) | 100% | `BN-012` |
| **P06** Analytics & executive dashboard | Executives, branch managers | English | Yes | **100% of labels and KPI names** | 100% | `BN-012` |
| **P07** Marketplace seller portal | 500–2,000 sellers | **Bengali** | Yes | **100%** | 100% | `BN-013` |
| **P08** Brand partner portal | 17+ brands, international | **English** | Yes | Labels only; correspondence English | 100% | `BN-013` |
| **P09** Logistics & rider app | 50–200 riders | **Bengali** | No — Bengali only at W3 | **100%** | Deferred to W8 | `BN-013` |
| **P10** Contact centre console | Agents | **Bengali** | Yes | **100%** | 100% | `BN-013` |
| **P11** Field auditor app | Auditors | **Bengali** | Yes | **100%** | 100% | `BN-013` |
| **P12** Partner & referral portal | Alliance partners | English | Yes | **100%** | 100% | `BN-013` |

| # | Rule |
|---|---|
| **LS-01** | **The default is a property of the surface, not of the user.** A user with no stored preference receives the surface default, always |
| **LS-02** | Where the default is Bengali, **the English build is the exception path**. Sprint planning that treats English as the baseline and Bengali as follow-up inverts `PS-03` and is a defect (`C-2`) |
| **LS-03** | `P09` ships **Bengali-only** at W3. An English toggle for riders has no identified audience and is deferred to W8 rather than built and left untranslated. This is a declared decision, not an omission (`BP-06`) |
| **LS-04** | A surface may not be accepted below **100%** Bengali completeness (`C-6`). 99% is a fail, not a near-pass (`BP-05`) |
| **LS-05** | Completeness is measured on **rendered surfaces**, not on bundle key counts. A key present but never rendered proves nothing; a rendered string missing from the bundle is caught only by rendering (`BN-018` §4) |

### 3.2 Non-portal surfaces

| Surface | Default | Bengali required | Owning file |
|---|---|---|---|
| SMS — customer, technician, finance, OTP | **Bengali**, from `fix.party.preferred_language` | **Yes — all 20 bilingual `NT` files** | `BN-014` |
| WhatsApp Business templates | Bengali | Yes — both language variants submitted to Meta separately | `BN-014` |
| Push notifications — `P01`, `P02`, `P09` | Follows the app's language | Yes | `BN-014` |
| Email — customer, corporate, seller, internal | Bengali for customer and internal; English for vendor and brand | Per `CG-010` §3.2 | `BN-014` |
| In-app notification inbox | Follows the surface | Yes | `BN-014` |
| IVR and voice prompts, hotline 16743 | **Bengali**, English on option 2 | **Yes — authored natively** | `BN-017` |
| Printed and PDF documents | **Bilingual layout** where the reader is a customer or employee | 34 of 44 `DT` files | `BN-015` |
| Statutory filings and court documents | **Bengali** | **Legal obligation** (`C-7`) | `BN-015` §6, pending §12 decision 4 |
| Labels, barcodes, QR (`DT-044`) | Bengali label text, Latin identifiers | Yes | `BN-015` |
| Help centre articles | Bengali | 18 of 20 `HC` files | `BN-016` |
| Training courses | Bengali; `TR-009` **Bengali-native** | 20 of 24 `TR` files | `BN-016` |
| Knowledge base articles | Bengali, often **Bengali-native** | 13 of 16 `KB` files | `BN-016` |
| Chatbot intents and utterances | **Both natively** | Yes | `BN-016` §5 |
| Reports and dashboards | Labels Bengali; data unchanged | 5 of 16 `RP` files | `BN-011` §6 |
| Master data display columns | Bengali `*_bn` column populated | 22 of 48 `MD` files | `BN-003` §7 |

---

## 4. Namespace ownership — closing the `common.*` gap

`UI-001` §3.3 allocates four namespace families. The `BN` register in the Master Index names a
Bengali bundle for `p01.*` … `p12.*` and for `ws.*`, **but for neither `common.*` nor `flow.*`.**

| Namespace | English pack | Bengali bundle in the register | Status |
|---|---|---|---|
| `p01.*` … `p12.*` | `UI-011`…`UI-022` | `BN-009`…`BN-013` | Owned |
| `ws.*` (14 admin workspaces) | `UI-023`…`UI-036` | `BN-011` | Owned |
| `flow.*` (6 critical flows) | `UI-037`…`UI-042` | Partly — `BN-009` covers "customer-facing flow copy" | **Partial** |
| **`common.*`** (9 cross-cutting packs, `UI-002`…`UI-010`) | `UI-002`…`UI-010` | **None** | **GAP** |

### 4.1 Why this is a `P0` defect and not a tidy-up

`common.*` holds the strings that `C-3` names explicitly. A sample from the English packs:
`common.error.field.imei_format`, `common.error.srm.tech_not_certified`,
`common.error.system.timeout`, `common.conflict.detected`, `common.confirm.order.cancel`,
`common.empty.no_results.search`, `common.a11y.live.sync`, `common.access.denied_record`.

Every one of those renders on `P02`. If no file owns their Bengali:

1. **`P02` cannot meet non-negotiable #3.** The bundle that `BN-010` owns is `p02.*`. The error
   the technician actually sees when a part is unavailable is `common.error.stock.unavailable`.
2. **Each portal translates the shared string separately**, producing five Bengali renderings of
   one English string — the exact failure `UI-001` `K-04` and `CP-01` exist to prevent, and the
   failure `CG-004` was written to stop happening in English.
3. **The offline and sync copy** (`UI-009`, `common.conflict.*`) is `common.*`. `P02`, `P09` and
   `P11` run offline for 24 hours; conflict messages are read at the worst moment, in the field.

### 4.2 Resolution

| # | Rule |
|---|---|
| **LS-06** | **A nineteenth `BN` file, `BN-019_Bengali_String_Bundle_Cross_Cutting_and_Critical_Flows`, must be registered** to own `common.*` and `flow.*`. Raised as a register change in `_AUDIT/AUDIT-012` finding **BN-01**; it is the Programme Content Lead's decision at a wave boundary, not this file's |
| **LS-07** | **Interim route, effective immediately.** Until `BN-019` is registered, `common.*` and `flow.*` Bengali is authored in **`BN-011` §6**, which is the earliest bundle (W1) and precedes every consumer. This is a **declared interim route** in the sense `AUDIT-009` established, not a permanent allocation |
| **LS-08** | **No portal bundle may contain a `common.*` or `flow.*` key.** A `common.*` key appearing in `BN-009`, `BN-010`, `BN-012` or `BN-013` is a duplication defect and fails `BN-018` `LQ-11` |
| **LS-09** | When `BN-019` is registered, the `common.*` and `flow.*` content moves out of `BN-011` **whole**, and `BN-011` retains a pointer. Content is never authored in two places (`CP-01`) |

---

## 5. Language resolution at runtime

The order in which the system decides what language to render. **Stop at the first rule that
resolves.**

| # | Source | Applies to | Persistence |
|---:|---|---|---|
| 1 | Explicit in-session toggle | All surfaces with a toggle | Session, then written to 2 or 3 |
| 2 | `res.users.lang` (internal user) | `P03`, `P06`, `P10`, `P11` | User record |
| 3 | `fix.party.preferred_language` (`MD-013`) | `P01`, `P04`, `P07`, `P12`, SMS, email, WhatsApp, push | Party record — **the source of truth for outbound messaging** |
| 4 | Device or browser locale | First visit, unauthenticated | Not persisted |
| 5 | **Surface default from §3** | Everything else | — |

| # | Rule |
|---|---|
| **LR-01** | **Outbound messaging always resolves at rule 3**, never at rule 4. A customer who once browsed in English from a borrowed phone must not receive English SMS for the next two years |
| **LR-02** | The toggle is **persistent and reversible in one action** from any screen (`UI-002`) |
| **LR-03** | Changing language **never** loses form state, navigation position or an in-progress transaction |
| **LR-04** | A public tracking link with no session resolves at rule 4, then rule 5 |
| **LR-05** | The language a document was **issued** in is stored on the document record and is not recomputed. A reprint reproduces the issued language (`BN-015` `DB-09`) |
| **LR-06** | Voice channel resolves by the caller's IVR selection for that call only; it does not write to the party record |
| **LR-07** | Where a bundle has no Bengali for a key, the system **raises a build failure**, it does not fall back to English at runtime. Silent fallback is how a surface reaches 97% and nobody notices (`UI-001` §5, `BN-005` `KP-09`) |

---

## 6. What is authored natively in Bengali

`CG-010` §4.2 names three types. This matrix confirms them and adds the reasoning that decides
future cases.

| Type | File | Why native, not translated |
|---|---|---|
| Field technician training | `TR-009`, planned in `BN-016` | 200–400 technicians, mixed literacy. Translated training teaches translated concepts |
| Contact centre and IVR scripts | `SP-034`, `NT-019`, delivered in `BN-017` | Spoken Bengali has a different rhythm. A translated script sounds wrong aloud |
| Chatbot utterances | `HC-017`, planned in `BN-016` §5 | Users type what they say. Translated utterances train on Bengali nobody uses |
| **Technician knowledge articles** | `KB` set, planned in `BN-016` §4 | **Added here.** `CG-010` §4 already records knowledge as "authored in Bengali where the author is a Bengali-speaking technician" but does not name it as a native type. Senior technicians are the scarce authoring resource (`AUDIT-008` R-07); requiring them to author in English first doubles the constraint |

| # | Rule |
|---|---|
| **NA-01** | For native content the **English version is the translation**, produced for review and governance, and is marked as such |
| **NA-02** | Native content still passes G4 — the reviewer checks register, terminology and clarity, not fidelity to an English source |
| **NA-03** | A type is native when **the translated artefact would not do the job**, not when Bengali is merely convenient. Convenience is a translation decision |
| **NA-04** | Native content is exempt from translation-memory leverage targets (`BN-008` §6) and is measured on review defect density instead |

### 6.4 Statutory Bengali — the 1987 Act

The Bangla Bhasha Prachalan Ain 1987 §3 requires records, correspondence and proceedings to be
in Bengali in courts, government and semi-government offices and autonomous institutions.

| Category of output | Position |
|---|---|
| Documents **filed with** NBR, a court, or a public body | **Bengali required by law.** English may accompany it |
| Documents **received from** a public body | Bengali; internal English summaries permitted |
| Statutory forms with a prescribed format — Mushak 6.1, 6.2, 6.3, 6.6, 9.1 | **The prescribed form governs.** Its own language and layout are not ours to change (`CG-004` `T-05`) |
| Commercial contracts with private counterparties | Unaffected by the Act; `CG-010` §4.1 governs |

> **This is a legal question and this file does not answer it.** §12 decision 4 routes it to
> Legal Counsel, and `BN-015` §6 holds the affected document list. It is recorded here because
> the localisation strategy cannot be complete while a statutory language obligation is
> unassessed.

---

## 7. Bengali as an input language

`NFR-016` is commonly read as an output requirement. It says **"interfaces, notifications,
reports and data entry"**. Data entry is the half that gets missed, and it is the half that
breaks search.

| # | Rule |
|---|---|
| **IN-01** | Every free-text field that may receive Bengali is **UTF-8 end to end** — client, transport, database, index, export, print (`05-06` §9) |
| **IN-02** | Bengali **phonetic input** is the norm (`NFR-074`). The system never requires a specific keyboard or IME |
| **IN-03** | Text is normalised to **Unicode NFC on write** (`BN-006` `EN-02`). Comparison, deduplication and indexing operate on the normalised form only |
| **IN-04** | Search and party matching tolerate spelling variation across phonetic renderings of the same name (`BN-003` §9, `MD-013` matching rules) |
| **IN-05** | Sorting and comparison use **ICU `bn-BD` collation** (`05-06` §9). Bengali does not sort by code point and must never be sorted by it |
| **IN-06** | Voice-to-text captures Bengali on `P02` (`NFR-074`, `04-00` §P02 Evidence). The stored transcript is Bengali; no automatic translation is applied (`CG-010` MT-01) |
| **IN-07** | Bilingual master data carries **both** an `name_en` and a `name_bn` column, and both are searchable (`MD-003`, `MD-006`, `MD-019`, `MD-021`) |
| **IN-08** | **Legacy Bijoy ASCII input is not accepted.** Bangladesh's national standards include the Bijoy coding system (BDS 1935:2018) alongside Unicode, and legacy ASCII text pasted from Bijoy renders as mojibake in a Unicode system. Migration and paste paths convert to Unicode or reject (`DM-011`, `BN-006` `EN-05`) |
| **IN-09** | Identifiers — reference numbers, IMEI, serial, BIN, TIN, phone — are **entered and stored in Latin script and Arabic numerals**, whatever the interface language (`BN-004` `DN-04`) |

---

## 8. Coverage by content type and owning `BN` file

The reverse index: given a body of English content, which `BN` file owns its Bengali.

| English content | Files | Bilingual | Owning `BN` file |
|---|---:|---:|---|
| `UI` cross-cutting `common.*` | `UI-002`…`UI-010` | 9 | **`BN-011` §6 interim → `BN-019`** (`LS-06`) |
| `UI` i18n standard | `UI-001` | 1 | `BN-005` is its counterpart; the file itself needs a `_BN` for translator use |
| `UI` portal packs | `UI-011`…`UI-022` | 12 | `BN-009`, `BN-010`, `BN-011`, `BN-012`, `BN-013` |
| `UI` admin workspaces | `UI-023`…`UI-036` | 14 | `BN-011` |
| `UI` critical flows | `UI-037`…`UI-042` | 6 | `BN-009` (customer) + **`BN-011` §6 interim** (`UI-041` admin) |
| `NT` all bilingual sets | 20 of 26 | 20 | `BN-014` |
| `NT` voice | `NT-019` | 1 | **`BN-017`** — not `BN-014`; see `AUDIT-012` **BN-04** |
| `DT` bilingual documents | 34 of 44 | 34 | `BN-015` |
| `SP` SOPs | 28 of 34 | 28 | `BN-016` §6 |
| `KB` knowledge | 13 of 16 | 13 | `BN-016` §4 |
| `TR` training | 20 of 24 | 20 | `BN-016` §3 |
| `HC` help and AI | 18 of 20 | 18 | `BN-016` §2, §5 |
| `LG` consumer- and employee-facing | 16 of 24 | 16 | `BN-015` §5 |
| `MD` display-value datasets | 22 of 48 | 22 | `BN-003` §7 — the `*_bn` columns |
| `VB` with Bengali content | 5 of 10 | 5 | Authored in place; terminology from `BN-003` |
| `TS`, `RP`, `CM`, `OP`, `EO`, `RF` | 38 of 96 | 38 | Authored in place; terminology from `BN-003` |
| `BN` own bilingual artefacts | 10 of 18 | 10 | Self |

> **The `BN` category owns wording for four bodies of content — `UI`, `NT`, `DT` and the help,
> training and knowledge plan — and owns *terminology and standards* for everything else.**
> That distinction is why the category is 18 files and the bilingual volume is 267.

---

## 9. Wave coverage gates

A wave gate that can actually be failed. Applied at the wave boundary by the Programme Content
Lead, evidenced by `BN-018` sign-off records.

| Wave | Surfaces going live | Bengali gate |
|:--:|---|---|
| **W1** | `P03`, admin workspaces, master data | `BN-002`, `BN-003`, `BN-004`, `BN-005`, `BN-006`, `BN-007` approved · `BN-011` at 100% including the interim `common.*` · every `*_bn` column populated in the 22 display datasets · `BN-018` **must be available**, see `AUDIT-012` **BN-02** |
| **W2** | `P01`, `P02`, customer notifications, help, training | `BN-009`, `BN-010` at 100% · `BN-014` covering all 20 bilingual `NT` files · `BN-015` for the W1–W2 `DT` set · `BN-016` plan approved and `TR-009` Bengali-native delivered · **`P02` fails the gate on a single English string** (`C-3`) |
| **W3** | `P09`, vendor, logistics | `BN-013` rider section at 100%, Bengali-only (`LS-03`) · `BN-014` finance and collections SMS |
| **W4** | `P04`, `P08`, `P10`, `P06` | `BN-012` at 100% · `BN-013` contact-centre section · `BN-017` recorded and in production |
| **W5** | Quality, finance depth, HR depth | `BN-015` payslip and HR letter set (`DT-041`, `DT-042`) — employee-facing, non-negotiable |
| **W6** | Native apps, AI assistant | `BN-016` §5 chatbot Bengali-native utterances · `BN-014` push libraries |
| **W7** | `P07`, `P12` | `BN-013` seller and partner sections at 100% |
| **W8–W9** | Scale, optimisation | `P09` English toggle (`LS-03` deferral closes) · full `BN-008` leverage review |

| # | Rule |
|---|---|
| **WG-01** | The gate is evidenced by **`BN-018` in-context sign-off records**, not by a bundle diff |
| **WG-02** | A wave gate failure on Bengali is a **wave failure**, treated identically to a functional failure. It is not a "content catch-up item" |
| **WG-03** | Translation capacity is escalated at **gate minus 6 weeks** (`CG-002` §7, `CG-010` §9) |
| **WG-04** | The gate is set by the **Bengali** sign-off date. A plan showing English completing at the gate has already missed it (`CG-007` §5, `CG-010` §9) |

---

## 10. Capacity consequence

| Item | Position |
|---|---|
| Bilingual files | **267** if `BN-019` is registered; 266 as the register currently stands |
| `BN` category estimate | 180–280 person-days (Master Index §7) — **excludes `BN-019`** |
| The estimate is volume-driven | It scales with `UI`, `NT` and `DT` output, not with the `BN` file count |
| Independence requirement | Translator and linguistic reviewer must be different people (`CO-05`). **Minimum two Bengali resources**, not one |
| Native-authoring resource | `TR-009`, `KB` articles and `SP-034` need **Bengali-speaking subject-matter authors**, who are not translators and cannot be substituted by them |
| Single point of failure | One Bengali resource across nine waves is the programme's most concentrated content risk (`CG-013` `CR-04`) |

---

## 11. Dependencies

| Depends on | Why |
|---|---|
| `CG-010` Bilingual Content Policy | The category-level decision this operationalises |
| `CG-004` Terminology Standard | The English terms `BN-003` binds |
| `UI-001` §3.3 Namespace allocation | The namespaces §4 assigns |
| `MD-013` Party master | `fix.party.preferred_language`, the rule-3 resolution source |
| `05-06` §9 | Locale, collation, encoding and acceptance standards |
| `BN-002` … `BN-018` | Every file in this category implements one row of §3 or §8 |

---

## 12. Open decisions

| # | Decision | Owner | Needed by | Blocks |
|---|---|---|---|---|
| 1 | **Register `BN-019`** for `common.*` and `flow.*` (`LS-06`) | Programme Content Lead | **Before W1 gate** | `P02` non-negotiable #3; `BN-011` scope |
| 2 | Bengali register — single standard register, or formal for Class A/B? Inherited from `CG-010` §12 item 1 | Localisation Lead, ratified by Content Lead | Before W1 | Every bundle. **`BN-002` proposes the answer** |
| 3 | Numerals — Bengali or Arabic glyphs by context. Inherited from `CG-010` §12 item 3 | Localisation Lead with Design | Before W1 | `BN-006`, `BN-007`, every bundle. **`BN-007` proposes the answer** |
| 4 | **Does the Bangla Bhasha Prachalan Ain 1987 §3 apply to the company's filings and, if so, to which documents?** (`C-7`, §6.4) | **Legal Counsel** with Tax Manager | Before the first statutory filing from the ERP | `BN-015` §6, `LG-024`, `DT-010`…`DT-014` |
| 5 | `P04` — is the UI bilingual while contractual documents stay English? Inherited from `CG-010` §12 item 4 | Account Management with Localisation | Before W4 | `UI-014`, `BN-012` |
| 6 | Translation sourcing — in-house, agency, or both, and how reviewer independence is guaranteed | Localisation Lead with Procurement | Before W1 | Capacity plan, `AF-09`, `BN-008` §3 |
| 7 | Is `P09`'s deferred English toggle acceptable to Logistics, or is it needed at W3? (`LS-03`) | `P09` owner with Logistics Director | Before W3 | `BN-013` scope and estimate |

---

## 13. Related documents

| Document | Relationship |
|---|---|
| [`../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) | The policy this operationalises |
| [`../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) | The English vocabulary `BN-003` binds |
| [`../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-001_UI_String_Architecture_and_i18n_Key_Standard.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-001_UI_String_Architecture_and_i18n_Key_Standard.md) | Namespace allocation |
| [`BN-002_Bengali_Translation_Standard.md`](BN-002_Bengali_Translation_Standard.md) | Register, honorifics, loanwords |
| [`BN-003_Bilingual_Terminology_Glossary.md`](BN-003_Bilingual_Terminology_Glossary.md) | The Bengali binding |
| [`BN-005_i18n_Key_Placeholder_and_Pluralisation_Rules.md`](BN-005_i18n_Key_Placeholder_and_Pluralisation_Rules.md) | `LR-07` build-failure rule |
| [`BN-011_Bengali_String_Bundle_P03_Admin.md`](BN-011_Bengali_String_Bundle_P03_Admin.md) | Holds the `common.*` interim route (`LS-07`) |
| [`BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md`](BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md) | The evidence §9 gates on |
| `05-06` §9 Localisation Standards | The technical floor |

---

## 14. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-17 | Initial issue. Seven commitments including the 1987 Act obligation newly identified; per-surface default and completeness matrix for twelve portals and fifteen non-portal surfaces; the `common.*` namespace gap identified and an interim route declared; seven-rule runtime language resolution; Bengali-as-input rules; nine wave gates; seven open decisions | Programme Content Lead (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Default, toggle and completeness stated for all twelve portals and every non-portal surface
- [x] Every commitment traced to a primary source with a verification date (`CM-R8`)
- [x] The `common.*` / `flow.*` namespace gap identified, quantified and given an interim route
- [x] Runtime language resolution ordered, with the outbound-messaging rule stated separately
- [x] Bengali stated as an **input** requirement, not only an output one (`NFR-016`)
- [x] Bengali-native content types named with the test for future cases
- [x] Wave gates written so they can be failed, with the evidence source named
- [x] All internal links resolve
- [x] Bengali counterpart — n/a; internal governance, English-only by `CG-010` §3.2
- [ ] **`BN-019` registration decision** — outstanding; §12 item 1
- [ ] **1987 Act applicability** — outstanding; §12 item 4, routed to Legal Counsel
- [ ] Named approver recorded — **pending Programme Content Lead**
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Decisions logged in `RF-006` — **outstanding; `RF-006` not yet written (`AF-04` analogue)**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
