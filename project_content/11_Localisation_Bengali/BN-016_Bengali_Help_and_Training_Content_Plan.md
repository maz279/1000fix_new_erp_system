---
id: BN-016
title: Bengali Help and Training Content Plan
project: 1000FiX ERP System v2.0
content_type: Plan
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Localisation Lead
author: Localisation with Learning & Development, Technical Services and Content Design
reviewers: [Learning & Development, Technical Director, Content Design Lead, Programme Content Lead, Quality Manager, Contact Centre Manager]
approver: Programme Content Lead with Learning & Development
content_class: E
purpose: >
  Decides, for the 79 bilingual files across help, training, knowledge and process content, which
  are translated from English, which are authored natively in Bengali, and in what order they are
  produced. Field technician training must be Bengali-native rather than translated: translated
  training teaches translated concepts, while native training teaches the job. The distinction is
  not a preference — it changes who authors the content, what skills they need, how it is
  reviewed, and whether the 775 to 1,545 unresourced specialist hours already identified in the
  KB category can be met at all.
traces_to: [HC-001, HC-002, HC-003, HC-004, HC-015, HC-016, HC-017, HC-018, HC-019, HC-020, TR-001, TR-002, TR-009, KB-001, SP-001, SP-034, BN-001 §6, BN-002, BN-003, BN-008, BN-017, BN-018, CG-010 §4.2, AUDIT-008 R-07]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: self — the plan is read by Bengali-speaking L&D and technician-trainer staff and is issued in both languages
sources:
  - source: project_content/00_Content_Governance_and_Standards/CG-010 §3.2 — KB 13 of 16 bilingual, TR 20 of 24, HC 18 of 20, SP 28 of 34; §4.2 three Bengali-native content types
    verified: 2026-08-17
    class: P1
  - source: project_content/08_Training_and_Enablement/08B_Course_Packs/TR-009 front matter — 200–400 field technicians, mixed literacy, high turnover, delivered in Bengali on the device they carry; the only P0 file in the TR category
    verified: 2026-08-17
    class: P1
  - source: project_content/_AUDIT/AUDIT-010 and Master Index §12 — Category 07 KB comprises specifications for content that does not exist; 160 articles, 22 tool guides and 48 reference cards enumerated and unwritten, estimated at 775–1,545 specialist hours, unresourced (AUDIT-008 R-07)
    verified: 2026-08-17
    class: P1
  - source: project_content/09_Help_Centre_and_Self_Service/HC-017 and HC-019 — conversational AI intents and guardrails; transcript-derived work at W2 has no confirmed basis under the Personal Data Protection Act 2026 (AUDIT-010 HC-01)
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# BN-016 — Bengali Help and Training Content Plan

> **The one decision this file exists to make: translated or native.**
>
> It looks like a sourcing preference. It is not. A translated course is authored by a training
> designer working in English and rendered by a translator. A **native** course is authored by a
> Bengali-speaking subject-matter expert — and for field repair, that person is a **senior
> technician**, who is the scarcest resource in the programme (`AUDIT-008` R-07) and cannot be
> substituted by a translator at any price.
>
> Deciding this late means discovering in month 12 that the training budget bought translation
> capacity and the training needs technician time.

---

## 1. Scope

| Category | Total | Bilingual | This plan covers |
|---|---:|---:|---|
| `HC` Help centre and self-service | 20 | **18** | §3 |
| `TR` Training and enablement | 24 | **20** | §4 |
| `KB` Knowledge base and technical library | 16 | **13** | §5 |
| `SP` Process, SOP and workflow | 34 | **28** | §6 |
| **Total** | **94** | **79** | |

The 15 English-only files are governance and architecture: `HC-001`, `HC-002`, `TR-001`–`TR-004`,
`KB-001`, `KB-002`, `KB-015`, `SP-001`–`SP-006`. **Declared, not omitted** (`CG-010` §3.2).

---

## 2. The translated / native decision

### 2.1 The test

| # | Rule |
|---|---|
| **HB-01** | Content is **native** when **the translated artefact would not do the job** — not when Bengali is merely convenient (`BN-001` `NA-03`) |
| **HB-02** | It fails to do the job when the content teaches **a physical skill, a spoken interaction, or a judgement** that the reader must perform in Bengali. Translation preserves the words and loses the performance |
| **HB-03** | It also fails when **the author is the Bengali speaker**. Requiring a senior technician to author in English and then translating back doubles a scarce constraint and loses accuracy twice |
| **HB-04** | For native content the **English is the translation**, produced for review and governance, and is marked as such (`BN-001` `NA-01`) |
| **HB-05** | Native content is **exempt from translation-memory leverage targets** and is measured on review defect density instead (`BN-008` `LV-05`) |
| **HB-06** | Native content still passes **G4** — the reviewer checks register, terminology and clarity, not fidelity to an English source (`BN-001` `NA-02`) |

### 2.2 The decision

| Content | Route | Author | Why |
|---|---|---|---|
| **`TR-009` Field technician course** | **Native** | Senior technicians (R12) with L&D | 200–400 technicians, mixed literacy, high turnover. `CG-010` §4.2 |
| **`KB` repair articles, tool guides, reference cards** | **Native** | Senior technicians | `HB-03`. **Extends `CG-010` §4.2, which names knowledge only conditionally** (`BN-001` §6) |
| **`SP-034` Contact centre scripts** | **Native** | Contact-centre supervisors | Spoken Bengali has a different rhythm. `CG-010` §4.2 |
| **`HC-017` Chatbot utterances** | **Native, both languages** | Content Design with agents | Users type what they say. `CG-010` §4.2 |
| **`HC-020` Video scripts** | **Native** | Content Design with a Bengali scriptwriter | Spoken, and the most expensive format to reshoot |
| `HC-003`…`HC-014` Help sets | Translated | Content Design → translator | Written reference; translation preserves it |
| `HC-015` FAQ bank | Translated, **Bengali questions sourced natively** | Content Design | The **answers** translate; the **questions** must be the ones users actually ask, in Bengali |
| `HC-016` In-product tour and coach marks | Translated | Content Design | Bound to UI strings (`BN-009`…`BN-013`) |
| `HC-018`, `HC-019` AI responses and guardrails | Translated | Content Design with Legal | Legal wording; consistency matters more than idiom |
| `TR-005`…`TR-024` other course packs | Translated | L&D → translator | Classroom and system training on documented processes |
| `SP-007`…`SP-034` SOPs | Translated | Process owners → translator | Procedural steps; translation preserves them |

> **Two extensions to `CG-010` §4.2 are made here and must be ratified with it.** `KB` articles
> and `HC-020` video scripts are added to the native list. `CG-010` §4 already treats knowledge as
> "authored in Bengali where the author is a Bengali-speaking technician" but does not name it as
> a native type; this plan makes that explicit, because the resourcing consequence is large.
> Recorded as `AUDIT-012` **BN-16**.

### 2.3 The resourcing consequence

| Route | Resource | Available? |
|---|---|---|
| Translated — 62 files | Professional Bengali translators plus independent reviewers (`CO-05`) | **Sourcing model undecided** (`BN-008` §11 item 1) |
| **Native — 17 files** | **Bengali-speaking senior technicians, contact-centre supervisors, a Bengali scriptwriter** | **Not resourced.** `AUDIT-008` R-07 already records 775–1,545 specialist hours as unresourced for `KB` alone |

> **This is the same finding `AUDIT-008` raised, now with its language dimension attached.** The
> `KB` hours were unresourced when the content was assumed to be English. Making them native does
> not increase the hours — it **removes the option of buying them from a translation vendor**.

---

## 3. Help centre — `HC`

| File | Route | Wave | Note |
|---|---|:--:|---|
| `HC-003` Help set `P01` | Translated | W2 | Highest-volume; **Bengali is the default help language** |
| `HC-004` Help set `P02` | Translated, **technician-reviewed** | W2 | Must use the exact `BN-010` strings |
| `HC-005` Help set `P03` | Translated | W1 | Branch and back-office |
| `HC-006`…`HC-014` Help sets `P04`–`P12` | Translated | W3–W7 | Per surface wave |
| `HC-015` FAQ bank | Translated answers, **native questions** | W2 | §2.2 |
| `HC-016` In-product tour | Translated | W2 | Bound to bundle strings |
| `HC-017` AI intents and utterances | **Native, both languages** | W6 | §7 |
| `HC-018` AI responses and fallback | Translated | W6 | |
| `HC-019` AI guardrails and disclosure | Translated, **Legal-reviewed in Bengali** | W6 | Class B wording |
| `HC-020` Video scripts | **Native** | W6 | §8 |

| # | Rule |
|---|---|
| **HC-B01** | **A help article names UI controls using the exact Bengali string from the bundle.** An article that says "অনুমোদন দিন" where the button says "অনুমোদন করুন" is wrong even though both are good Bengali (`BN-018` `LQ-12`) |
| **HC-B02** | **Bengali help is searchable phonetically** (`BN-003` §14). A help centre that only matches exact spelling is unusable for users typing with Avro |
| **HC-B03** | Help articles are read **on a phone, on 3G** (`PS-07`). Bengali web fonts are heavy; the help centre uses the same bundled or cached face and does not re-download per page |
| **HC-B04** | Numerals in help **prose** are Bengali; numerals in **steps that quote a field value** are Arabic (`BN-007` §3.2, §3.3) |
| **HC-B05** | **Screenshots are language-specific.** A Bengali article showing an English screenshot teaches the wrong screen (`MM-002`) |

---

## 4. Training — `TR`

| File | Route | Wave | Delivery language |
|---|---|:--:|---|
| **`TR-009` Field technician** | **Native Bengali** | **W2** | **Bengali, on the device** |
| `TR-007`, `TR-008` Service agent, dispatcher | Translated | W2 | Bengali |
| `TR-010`…`TR-014` Branch, workshop, inventory, procurement, finance | Translated | W1–W3 | Bengali |
| `TR-016` Auditor | Translated | W4 | Bengali |
| `TR-017` Contact centre | Translated, **script sections native** | W4 | Bengali |
| `TR-019`, `TR-020` Seller, rider | Translated | W3–W7 | Bengali |
| `TR-021`…`TR-024` Remaining packs | Translated | W3–W5 | Per pack |

| # | Rule |
|---|---|
| **TR-B01** | **`TR-009` is authored in Bengali by senior technicians and rendered into English afterwards** (`HB-04`). A Bengali translation of an English course is **not** compliance with this rule |
| **TR-B02** | **Assessment questions are native in every course delivered in Bengali.** A translated multiple-choice question frequently has two defensible Bengali answers where the English had one |
| **TR-B03** | Course content **quotes the bundle strings verbatim** (`HC-B01`) |
| **TR-B04** | **Training is delivered on the device the learner uses at work** — `P02` for technicians (`M22` FR-LMS-025), branch hardware for agents |
| **TR-B05** | **Low-literacy design applies**: short sentences, one instruction per step, visual before textual, audio option. This is a **content** requirement, not an accessibility add-on |
| **TR-B06** | **`TR-025` — the Layer 1 statutory induction curriculum for 800+ employees — has no owning file** (`AUDIT-009` TR-01, Master Index §12). When registered it is **bilingual and mandatory**, and this plan must be reissued to cover it |

---

## 5. Knowledge base — `KB`

**The category with the largest unresourced gap in the register, now with a language constraint
attached.**

| Asset | Volume | Route | Author |
|---|---:|---|---|
| Repair articles | **160** | **Native Bengali** | Senior technicians |
| Tool guides | **22** | **Native Bengali** | Senior technicians |
| Reference cards | **48** | **Native Bengali** | Senior technicians |
| `KB-001`, `KB-002`, `KB-015` governance | 3 files | English-only | Knowledge Manager |

| # | Rule |
|---|---|
| **KB-B01** | **Repair knowledge is authored in Bengali by the person who has the knowledge** (`HB-03`). There is no route in which a translator produces a repair procedure |
| **KB-B02** | Articles are read **offline, inside `P02`** (`04-00` §P02 Knowledge). Bengali text and any bundled diagrams are packaged with the app (`BN-005` `BU-04`) |
| **KB-B03** | **Device, part and fault names come from `MD-021`, `MD-022` and `MD-024` `name_bn`** (`BN-003` §12). Model numbers stay Latin (`BN-004` `BR-01`) |
| **KB-B04** | **Safety content within a repair article follows `BN-010` §4** — direct, unhedged, at the safety size (`SF-01`) |
| **KB-B05** | An article authored in Bengali is **reviewed by a second technician**, not only by a linguist. Technical accuracy and linguistic quality are different reviews |
| **KB-B06** | The English rendering is produced **after** Bengali approval, for governance and for non-Bengali-speaking engineers (`HB-04`) |

> **The unresourced hours are the plan's biggest risk.** `AUDIT-008` R-07 estimates 775–1,545
> specialist hours for the `KB` content and records them as unresourced. Those are now
> **Bengali-speaking senior technician** hours, drawn from the same 200–400 population that is
> also the audience for `TR-009` and the operator of `P02`. Escalated in §10.

---

## 6. Process and SOP — `SP`

| Route | Files | Note |
|---|---|---|
| Translated | 28 SOPs (`SP-007`…`SP-034`) | Procedural steps translate well |
| **Native** | **`SP-034` contact centre scripts** | Spoken content (`CG-010` §4.2) |
| English-only | `SP-001`…`SP-006` | Process architecture for head office |

| # | Rule |
|---|---|
| **SP-B01** | **SOPs are executed at 51+ branches by Bengali-speaking staff.** A translated SOP is acceptable; an untranslated one is not |
| **SP-B02** | SOP step wording **quotes the bundle strings** for any system action (`HC-B01`) |
| **SP-B03** | An SOP that carries a **legal or statutory obligation** — cash handling, custody, data destruction — uses the formal sub-register (`BN-002` `RD-C`) and is Legal-reviewed in Bengali |
| **SP-B04** | **`SP-034` is native and feeds `BN-017`.** The written script and the spoken prompt must be the same Bengali (`BN-017` `VP-02`) |

---

## 7. Conversational AI — `HC-017`, `HC-018`, `HC-019`

| # | Rule |
|---|---|
| **AI-B01** | **Utterances are native in both languages** (`CG-010` §4.2). Translated utterances train the model on Bengali nobody types |
| **AI-B02** | Bengali utterances must include **phonetic spelling variants, transliterated English, and code-mixed input** — "AC ঠান্ডা হচ্ছে না", "ac thanda hocche na", "এসি ঠান্ডা হয় না" are one intent |
| **AI-B03** | **Romanised Bengali (Banglish) is a first-class input form.** A large share of Bangladeshi users type Bengali in Latin script. An intent model trained only on Bengali script will fail on them |
| **AI-B04** | **Machine translation inside the assistant is conditional**, requires an AI disclosure (`HC-019`), and may not commit the company to a price, promise or legal position (`CG-010` §6.2) |
| **AI-B05** | **`AUDIT-010` HC-01 is unresolved**: transcript-derived work at W2 has no confirmed basis under the Personal Data Protection Act 2026. **Mining Bengali customer utterances is the same processing activity** and is blocked on the same decision |
| **AI-B06** | Fallback and handover copy is translated, and the **handover to a human states the language the agent will use** |

---

## 8. Video and multimedia — `HC-020`, `MM`

| # | Rule |
|---|---|
| **VD-B01** | Scripts are **native Bengali** (§2.2). A translated script sounds translated when read aloud |
| **VD-B02** | **Subtitles are burned-in-free, real text**, in Bengali, and are separately reviewed. Bengali subtitle rendering fails differently from body text (`BN-006` §9) |
| **VD-B03** | **On-screen UI in a video must be the Bengali build**, not the English one (`HC-B05`) |
| **VD-B04** | Voice-over direction follows `BN-017` §4 — standard Bengali, place names as locally pronounced, digits read individually |
| **VD-B05** | **A wording change after production is a reshoot.** Video is the most expensive format to correct, which is why the script passes G4 **before** recording, not after |

---

## 9. Sequencing

Ordered by **when the audience needs it**, not by category.

| Wave | Bengali help, training and knowledge required |
|:--:|---|
| **W1** | `TR-010`…`TR-014` branch and back-office courses · `HC-005` `P03` help · `SP-007`…`SP-020` branch SOPs |
| **W2** | **`TR-009` native technician course** · `HC-003`, `HC-004` help sets · `HC-015` FAQ · `HC-016` tour · `TR-007`, `TR-008` · first 40 `KB` articles for the highest-volume device families |
| **W3** | `TR-019`, `TR-020` seller and rider · `HC-007`, `HC-011` · `SP` logistics SOPs |
| **W4** | `TR-016`, `TR-017` · `HC-006`, `HC-008`, `HC-010`, `HC-012`, `HC-013` · **`SP-034` native scripts → `BN-017`** |
| **W5** | `TR-021`…`TR-024` · `SP` quality and HR SOPs · next 60 `KB` articles |
| **W6** | **`HC-017` native utterances** · `HC-018`, `HC-019` · `HC-020` video scripts · remaining `KB` |
| **W7** | `HC-009`, `HC-014` seller and partner help |

| # | Rule |
|---|---|
| **SQ-01** | **Training precedes go-live for its audience, and Bengali training precedes it by the G4 service level plus rework** (`CG-007` §6) |
| **SQ-02** | **`KB` is produced in device-family priority order**, highest service volume first. 160 articles cannot be produced in one wave and pretending otherwise is how none get produced |
| **SQ-03** | **Help follows the surface it documents by no more than one sprint.** Help that lags the build documents a screen that no longer exists |

---

## 10. Risks and escalations

| # | Risk | Consequence | Escalation |
|---|---|---|---|
| **R-1** | **Native `KB` authoring is unresourced** — 775–1,545 senior-technician hours (`AUDIT-008` R-07), now not purchasable from a translation vendor | 160 articles unwritten; `P02` offline knowledge empty; first-time-fix target unsupported | **Technical Director with Programme Director.** `CG-013` escalation |
| **R-2** | **`TR-009` native authoring competes for the same technicians** | Either the course or the knowledge base slips | Technical Director |
| **R-3** | Translation capacity for 62 files across nine waves is a single point of failure (`CG-013` `CR-04`) | Wave gates missed on Bengali | Localisation Lead, at gate minus 6 weeks (`CG-002` §7) |
| **R-4** | **`AUDIT-010` HC-01** — the PDPA 2026 basis for transcript- and utterance-derived work is unconfirmed | `HC-015`, `HC-017` collection cannot lawfully begin | **Legal Counsel with CDO**, `CG-013` trigger |
| **R-5** | **`TR-025` statutory induction has no owning file** (`AUDIT-009` TR-01) | 800+ employees with no registered statutory induction, in either language | Programme Content Lead |
| **R-6** | Low-literacy design (`TR-B05`) is a content skill the programme has not sourced | Training that is Bengali but still unusable | L&D |

---

## 11. Effort

Stated as a range with a basis (`RG-05`). **Not a commitment.**

| Route | Files | Basis | Estimate |
|---|---:|---|---|
| Translated `HC`, `TR`, `SP` | 62 | Volume-driven; leverage rises after W2 (`BN-008` §6.2) | Within the `BN` category's 180–280 person-days |
| **Native `TR-009`** | 1 course | Senior-technician authoring plus L&D design | **20–35 technician-days** |
| **Native `KB`** | 230 assets | `AUDIT-008` R-07 | **775–1,545 specialist hours ≈ 100–195 technician-days** |
| **Native `SP-034`, `HC-017`, `HC-020`** | 3 | Supervisor and scriptwriter time | **25–40 days** |
| **Native total** | — | — | **≈ 145–270 specialist days, outside the `BN` estimate and outside the business case** |

> **The native total is not in the `BN` category's 180–280 person-day estimate**, because it is not
> localisation effort — it is subject-matter-expert effort that happens to be in Bengali. It
> compounds audit finding **AF-09** and must be raised at the same Steering Committee item.

---

## 12. Open items

| # | Item | Owner | Blocks |
|---|---|---|---|
| 1 | **Ratify the two extensions to `CG-010` §4.2** — `KB` articles and `HC-020` scripts as native types (§2.2) | Programme Content Lead with Localisation Lead | The resourcing decision in §10 R-1 |
| 2 | **Resource native `KB` and `TR-009` authoring** | **Technical Director with Programme Director** | 160 articles, `P02` offline knowledge, `TR-009` |
| 3 | **`AUDIT-010` HC-01 PDPA basis** | Legal Counsel with CDO | `HC-015`, `HC-017` |
| 4 | **`TR-025` registration** | Programme Content Lead | 800+ employees' statutory induction |
| 5 | Translation sourcing model (`BN-008` §11 item 1) | Localisation Lead with Procurement | 62 translated files |
| 6 | `BN-002` and `BN-007` ratification | Programme Content Lead | All content |
| 7 | Low-literacy content design capability (`R-6`) | L&D | `TR-009`, `KB` |

---

## 13. Related documents

| Document | Relationship |
|---|---|
| [`../08_Training_and_Enablement/08B_Course_Packs/TR-009_Course_Pack_Field_Technician.md`](../08_Training_and_Enablement/08B_Course_Packs/TR-009_Course_Pack_Field_Technician.md) | The native course this plan governs |
| [`../09_Help_Centre_and_Self_Service/09A_Help_Sets_By_Portal/HC-004_Help_Set_P02_Technician_App.md`](../09_Help_Centre_and_Self_Service/09A_Help_Sets_By_Portal/HC-004_Help_Set_P02_Technician_App.md) | The help set bound to `BN-010` |
| [`../09_Help_Centre_and_Self_Service/09B_Conversational_AI/HC-017_Conversational_AI_Intent_and_Utterance_Library.md`](../09_Help_Centre_and_Self_Service/09B_Conversational_AI/HC-017_Conversational_AI_Intent_and_Utterance_Library.md) | Native utterances, and the PDPA question |
| [`BN-010_Bengali_String_Bundle_P02_Technician.md`](BN-010_Bengali_String_Bundle_P02_Technician.md) | The strings help and training must quote |
| [`BN-017_Bengali_Voice_IVR_and_Speech_Prompt_Pack.md`](BN-017_Bengali_Voice_IVR_and_Speech_Prompt_Pack.md) | Where `SP-034` native scripts are spoken |
| [`BN-008_Translation_Memory_and_Term_Base_Management.md`](BN-008_Translation_Memory_and_Term_Base_Management.md) | Leverage exemption for native content |
| [`../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) | §4.2, extended here |

---

## 14. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-17 | Initial issue. Translated-versus-native decided for all 79 bilingual files against a stated test; **`KB` articles and `HC-020` video scripts added to the native list, extending `CG-010` §4.2**; the resourcing consequence made explicit — native content cannot be bought from a translation vendor; romanised Bengali named as a first-class chatbot input; wave sequencing ordered by audience need; six risks with named escalations; **a native effort estimate of 145–270 specialist days shown to sit outside both the `BN` estimate and the business case** | Programme Content Lead with Learning & Development (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Translated-versus-native decided for **every** bilingual file, against a stated and reusable test
- [x] The two extensions to `CG-010` §4.2 declared and routed for ratification rather than assumed
- [x] **The resourcing consequence stated plainly** — native content is subject-matter-expert time, not translation spend
- [x] Help, training, knowledge, process, AI and video each given their own rules
- [x] Romanised Bengali named as a required chatbot input class
- [x] Sequencing ordered by audience need with the training-precedes-go-live rule
- [x] Risks carry named escalation owners, and the two open audit findings they inherit are cited
- [x] Effort stated as a range with a basis, and its position outside the business case stated (`AF-09`)
- [x] All internal links resolve
- [ ] **Native authoring resourced** — **outstanding; §12 item 2, the single largest risk in this plan**
- [ ] **`CG-010` §4.2 extensions ratified** — outstanding; §12 item 1
- [ ] **`AUDIT-010` HC-01 PDPA basis confirmed** — outstanding; blocks `HC-015` and `HC-017`
- [ ] **`TR-025` registered** — outstanding
- [ ] Bengali counterpart of this plan issued — **outstanding**; the plan is bilingual per `CG-010` §3.2
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
