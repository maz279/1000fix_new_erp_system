---
id: HC-001
title: Help Centre Information Architecture
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design
author: Content Design with Knowledge Management and Customer Experience
reviewers: [Knowledge Manager, Customer Service Manager, CTO, BI Lead, Localisation Lead, Accessibility reviewer, Programme Content Lead]
approver: Content Design Lead with Customer Service Manager
content_class: E
purpose: >
  Defines the per-audience help structure, the category tree, search behaviour, the article-type
  taxonomy and the cross-linking rules for eleven help audiences across twelve portals. Eleven
  audiences cannot share one help tree, and they cannot each be given an unplanned one; without a
  declared architecture the help centre becomes twelve unrelated content sets that cannot be
  searched, measured or maintained together.
traces_to: [M61, M32, M27, M34, P01, P02, P03, P04, P05, P06, P07, P08, P09, P10, P11, P12, KB-001, KB-015, HC-002, HC-015, HC-016, HC-017, CG-004, CG-011, CG-014, RP-001]
priority: P1
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P01 targets more than 80% of status enquiries handled without a hotline call; twelve portals with distinct audiences
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §5.2 FR-KMS-022 customer self-help served in P01 with symptom-led navigation, in Bengali, on a 3G connection; §9 BRU-KMS-11 customer-facing derivatives have a separate approval and an internal edit never propagates automatically
    verified: 2026-08-18
    class: P1
  - source: project_content/07_Knowledge_Base_and_Technical_Library/KB-001_Knowledge_Architecture_and_Tagging_Standard.md §4.4 mandatory tagging spine and O-04 — the decision on whether the help centre reuses the KB facets is explicitly deferred to this file
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 — KPI-025 status enquiries deflected to self-service 60% at W7 and 80% at W9; KPI-026 AI first-contact resolution 40% then 55%; KPI-027 first-contact resolution all channels 70% then 78%
    verified: 2026-08-18
    class: P1
  - source: Knowledge-Centered Service (KCS) practice — self-service success depends on content being findable in the customer's own words rather than in the organisation's vocabulary; findability is an architecture property, not a search-engine property
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# HC-001 — Help Centre Information Architecture

> **Read this before writing any other `HC` file.** Every help set in `09A`, the FAQ bank, the
> in-product help and the conversational AI content all inherit their structure, their tagging and
> their findability rules from this document.
>
> **It also settles a decision deferred to it from another category.** `KB-001` `O-04` records:
> *"Whether `HC-001` reuses these facets or defines its own customer-facing taxonomy. Two taxonomies
> over one corpus is the drift `CP-01` exists to prevent."* §4.4 decides it.

---

## 1. Purpose

`P01` commits to **more than 80% of status enquiries handled without a hotline call**. That is not a
booking-engine target; it is a content-findability target. `KPI-025` puts the same commitment on the
programme scoreboard at 60% by W7 and 80% by W9.

Deflection at that level fails for one of three reasons, and all three are architecture failures:

| Failure | What the customer experiences | Root cause |
|---|---|---|
| The answer does not exist | Search returns nothing | Coverage gap — measurable only if the architecture defines what coverage means |
| The answer exists and is not found | Search returns the wrong thing, or twelve things | **Findability** — the customer searched in their words, the content is filed in ours |
| The answer is found and is not understood | The customer reads it and calls anyway | Reading level, language, or an article written for the wrong audience |

**Consequence of absence (`CP-03`).** Without this file: twelve portal help sets authored to twelve
structures; a search index over content with no common facets; no definition of coverage, so
`KPI-025` cannot be diagnosed when it misses; customer-facing derivatives drifting from their `KB`
sources; and `M32` grounded on a corpus whose boundary nobody declared.

---

## 2. Scope

**In scope:** the audience model; the help object types; the category tree and its per-audience
projection; **the tagging decision inherited from `KB-001` `O-04`**; findability design — search,
symptom-led navigation, contextual surfacing; the customer-derivative boundary with `KB`;
cross-linking rules; coverage and deflection measurement; and rules `IA-01`…`IA-20`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Article structure, step numbering, screenshot rules | [`HC-002_Help_Article_Template_and_Style_Rules.md`](HC-002_Help_Article_Template_and_Style_Rules.md) |
| The help content itself | `HC-003`…`HC-014` in `09A_Help_Sets_By_Portal/` |
| FAQ curation | [`HC-015_FAQ_Bank_by_Audience.md`](HC-015_FAQ_Bank_by_Audience.md) |
| In-product tours and coach marks | [`HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md`](HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md) |
| Conversational AI intents, responses and guardrails | `09B_Conversational_AI/` — `HC-017`, `HC-018`, `HC-019` |
| **Internal technical knowledge** — repair procedures, fault codes, safety data | `KB-*`; **`M61` §3.2 keeps the boundary and §4.5 below restates it** |
| Knowledge tagging, currency and the `M32` corpus admission test | [`../07_Knowledge_Base_and_Technical_Library/KB-001_Knowledge_Architecture_and_Tagging_Standard.md`](../07_Knowledge_Base_and_Technical_Library/KB-001_Knowledge_Architecture_and_Tagging_Standard.md) · [`../07_Knowledge_Base_and_Technical_Library/KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md`](../07_Knowledge_Base_and_Technical_Library/KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md) |
| UI copy, empty states, error messages | `UI-*` — **help explains the task; UI copy performs it** |
| Training courses | `TR-*`; `TR-022` job aids are for trained users, help is for anyone |
| Portal search implementation and ranking code | `M61` T-05/T-06; this file states the requirement |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Content Design** | Structure twelve help sets to one architecture |
| **Knowledge Manager** | Operate the `KB` → `HC` derivative boundary (`BRU-KMS-11`) |
| **Customer Service Manager** | Own the deflection outcome and the customer-facing approval |
| **AI team** | Know what the `M32` customer corpus contains and where its boundary is |
| **BI Lead** | Compute coverage and deflection (`KPI-025`) |
| **Portal owners** | Understand what help their surface needs and who writes it |
| **Localisation Lead** | Plan 18 bilingual files against a declared structure |

---

## 4. Content

### 4.1 The audience model — and a register discrepancy

The register's justification for this file says *"**eleven** audiences cannot share one help tree"*.
Enumeration finds **twelve portal help sets** (`HC-003`…`HC-014`) and, counting distinct human
audiences rather than portals, **eleven**:

| # | Audience | Portal(s) | Help set | Population |
|---:|---|---|---|---|
| 1 | **Customer** | `P01` | `HC-003` | 250,000+/month |
| 2 | **Field technician** | `P02` | `HC-004` | 200–400 |
| 3 | **Internal operations user** | `P03` | `HC-005` | 150–250 |
| 4 | **Corporate customer administrator** | `P04` | `HC-006` | 500–2,000 |
| 5 | **Vendor / supplier** | `P05` | `HC-007` | 200–500 |
| 6 | **Marketplace seller** | `P07` | `HC-009` | 500–2,000 |
| 7 | **Brand partner** | `P08` | `HC-010` | 17+ organisations |
| 8 | **Rider / logistics** | `P09` | `HC-011` | 60–175 |
| 9 | **Contact centre agent** | `P10` | `HC-012` | 34–70 |
| 10 | **Field auditor** | `P11` | `HC-013` | 20–60 |
| 11 | **Referral / channel partner** | `P12` | `HC-014` | Varies |
| — | *Analytics consumer* | `P06` | `HC-008` | **Not a distinct audience — a mode of use by audiences 3, 4 and 7** |

**`IA-01`: `P06` analytics help serves existing audiences in a different mode, not a twelfth
audience.** That is why the register says eleven audiences and twelve help sets, and both are
correct. Recorded explicitly so a later reader does not "fix" one into the other. Raised as audit
finding **HC-06** for a clarifying note in the register row.

### 4.2 Help object types

**`IA-02`: five object types. The set is closed; an author may not invent one.**

| # | Object | Code | Answers | Governed by |
|---:|---|---|---|---|
| 1 | **Task article** | `HLP-` | *"How do I do this?"* | `HC-002` |
| 2 | **Concept article** | `HLP-` | *"What is this and why does it work this way?"* | `HC-002` |
| 3 | **Troubleshooting article** | `HLP-` | *"It isn't working — what now?"* | `HC-002` |
| 4 | **FAQ item** | `FAQ-` | *"Quick answer to a question people actually ask"* | `HC-015` |
| 5 | **In-product help** | `TIP-` | Tours, coach marks, contextual tips | `HC-016` |

Two further object classes are consumed by the help centre but **owned elsewhere**, and the
distinction is load-bearing:

| Object | Owned by | Relationship |
|---|---|---|
| `KNW-` knowledge article | `KB-001` | **A customer help article may derive from one; it is never the same record** (`BRU-KMS-11`) |
| Video script | [`HC-020_Video_Tutorial_Script_Library.md`](HC-020_Video_Tutorial_Script_Library.md) | Scripts here; produced assets in `MM-007` |

### 4.3 The category tree

**One tree, projected per audience.** `IA-03`: there is a single canonical category tree; each
audience sees the branches relevant to it, in an order set for it. There are not eleven trees.

| L1 category | Applies to | Contains |
|---|---|---|
| **Getting started** | All | Account, access, first use, navigation |
| **Booking and requests** | 1, 4, 6 | Create, amend, cancel, schedule |
| **Tracking and status** | 1, 4, 6, 9 | Where is it, what happens next, ETA |
| **Doing the work** | 2, 3, 8, 10 | Job execution, manifest, audit execution |
| **Money** | 1, 4, 5, 6, 7, 11 | Prices, invoices, payments, earnings, claims |
| **Warranty and cover** | 1, 4, 7 | Warranty, contracts, protection plans |
| **Products and parts** | 1, 5, 6 | Catalogue, availability, compatibility |
| **My account and data** | All | Profile, preferences, **privacy and data rights** |
| **Problems and complaints** | All | Troubleshooting, escalation, complaint |
| **Policies and terms** | All | Links to `LG-*`; **help never restates a legal term** (`IA-14`) |

**`IA-04`: maximum depth is three levels.** L1 category → L2 topic → article. A customer who has to
open four folders has already called.

### 4.4 The tagging decision — resolving `KB-001` `O-04`

**Decision: the help centre reuses the `KB-001` facet spine wherever the facet exists, and adds
four help-specific facets. It does not define a parallel taxonomy.**

| `KB-001` facet | Reused in `HC`? | Note |
|---|:--:|---|
| 1 `device_family` | ✔ | Same values, `MD-021` |
| 2 `model_scope` | ✔ | Rarely populated on customer help; used on troubleshooting |
| 3 `brand` | ✔ | `MD-017` |
| 4 `fault_code` | ✔ | **The join that lets a customer symptom reach a technical article's customer derivative** |
| 5 `resolution_code` | ✖ | Internal only; meaningless to a customer |
| 6 `repair_level` | ✖ | Internal only |
| 7 `hazard_class` | ✔ | **Retained** — customer safety guidance exists (`KB-001` §4.2 permits a `safety_note` derivative) |
| 8 `audience` | ✔ | **The boundary facet.** `KB-001` `KA-08` already makes `customer` a value |

**Four help-specific facets are added:**

| Facet | Values | Why it cannot be a `KB` facet |
|---|---|---|
| `help_audience` | The eleven audiences in §4.1 | `KB`'s `audience` facet has three values and governs publication; this one governs *navigation* |
| `portal` | `P01`…`P12` | Help is surfaced in a portal; knowledge is not |
| `journey_stage` | discover · book · wait · receive · pay · after | The customer's timeline, which has no internal equivalent |
| `object_type` | §4.2 | Distinguishes task from concept from FAQ |

**`IA-05`: no help facet duplicates a `KB` facet under a different name.** Where a facet exists in
`KB-001`, the help centre uses it with the same values from the same register (`KA-02`).

> **Why reuse rather than a fresh taxonomy — the reasoning, so it can be re-examined.**
> A separate customer taxonomy is superficially attractive: customer vocabulary differs from
> technical vocabulary, and the facets would be simpler. It was rejected for three reasons.
> **First**, one corpus with two taxonomies is exactly the drift `CP-01` prohibits, and
> `KB-001` `O-04` flagged it before either was written. **Second**, `M32` grounds on both `KB` and
> `HC` content (`FR-CAI-015`); two facet schemes means two retrieval paths and two places for the
> corpus boundary to leak. **Third**, the `fault_code` facet is what allows a customer describing a
> symptom to reach the customer-safe derivative of the technical article that solves it — the single
> highest-value join in the content set, and it only exists if both sides use `MD-024`.
>
> The customer-vocabulary problem is real and is solved differently: by **`symptom_phrase_bn`**
> (`KB-001` §4.5) and by `HC-015`'s FAQ bank sourced from what customers actually asked — not by a
> second taxonomy.

### 4.5 The `KB` → `HC` derivative boundary

`M61` §9 `BRU-KMS-11` is a hard rule: **customer-facing derivatives have a separate approval, and an
internal edit never propagates to customers automatically.**

| | `KB-*` knowledge article | `HC-*` help article |
|---|---|---|
| Reader | Technician, agent, auditor | Customer, partner, external user |
| Assumed competence | Trained and certified | **None** |
| Language register | Technical, precise | Plain, `CG-011` reading level |
| Safety content | Full hazard data | **Only what a consumer may safely act on** |
| Approval | Technical reviewer + HSE where relevant | **Quality Manager + Customer Service Manager** (`BRU-KMS-11`) |
| Record | `KNW-nnnnn` | **`HLP-nnnnn` — a separate record** |
| On source change | — | **Flagged for review, never auto-updated** |

**`IA-06`: a customer help article that derives from a `KNW-` article names its source and its
source version.** When the source is revised, superseded or retired (`KB-015` §4.4), the derivative
is flagged — not changed, and not left unflagged.

**`IA-07`: a customer article never instructs a consumer to perform a procedure that `KB-013`
classifies as a hazard requiring competence.** The derivative says what to do *instead* — isolate,
stop using, bring it in. This is the rule that stops a well-meant troubleshooting article telling a
customer to open a microwave.

### 4.6 Findability — three paths

`M61` §4 states the design position for knowledge: search is the fallback, not the path. **For the
help centre the ordering is different**, because a customer arrives without context the system can
use.

| Path | Trigger | Design requirement |
|---|---|---|
| **1 — Contextual** | The user is on a screen and needs help with *this* | In-product help (`HC-016`); article surfaced from the screen's `portal` + `journey_stage` facets |
| **2 — Symptom-led navigation** | The customer knows what is wrong, not what it is called | **`FR-KMS-022` requires symptom-led navigation, in Bengali, on a 3G connection.** Entry by symptom, not by category |
| **3 — Search** | Everything else | Bilingual, typo-tolerant, transliteration-aware |

**`IA-08`: symptom-led navigation is a first-class entry point, not a search feature.** A customer
whose air conditioner is not cooling does not know whether that is "Troubleshooting", "Warranty" or
"Booking". The symptom list is the front door, and it binds to `MD-024` `SYM-` codes with their
Bengali descriptions — the `is_customer_selectable` flag in `MD-024` §2 exists for exactly this.

**`IA-09`: help must be usable on a 3G connection on a low-end Android.** Page weight, image count
and font loading are architecture constraints, not optimisations.

### 4.7 Cross-linking

| # | Rule | Class |
|---|---|:--:|
| **IA-10** | Every article links to **at most five** related articles. A link list longer than five is a category, not a set of links | **S** |
| **IA-11** | Cross-links are within the audience's projection; a customer article never links to an internal `KB` article | **H** |
| **IA-12** | An article that would need to explain another concept links to it rather than restating it (`CP-01`) | **H** |
| **IA-13** | Every article ends with a route to a human — the correct one for that audience and journey stage | **H** |
| **IA-14** | Help **never restates a legal term**. It links to the `LG-*` artefact and summarises only what is operationally necessary, marked as a summary | **H** |
| **IA-15** | An article referencing a price, a fee or an SLA links to the authoritative source and does not state the figure (`BRU-CAI-02` pattern) | **H** |

> **`IA-13` is the rule that makes deflection honest.** A help centre optimised only to prevent
> contact will trap the customer who genuinely needs a person. Every article carries an exit, and
> `KPI-027` first-contact resolution is measured alongside `KPI-025` deflection precisely so that
> one is not bought with the other.

### 4.8 The `M32` corpus boundary

`M32` `FR-CAI-015` requires every substantive answer to be grounded in retrieved content and
`BRU-CAI-01` blocks ungrounded factual output. The help centre is half of that corpus; `KB` is the
other half.

| Corpus admission test | Applied to `HC` content |
|---|---|
| State is `Published` | Article state |
| Within its review cycle | `HC-002` review cadence |
| `help_audience` matches the asking surface | Facet §4.4 |
| Customer-approved where the surface is customer-facing | `BRU-KMS-11` approval recorded |
| Not a legal term restated | `IA-14` |
| Not a price, fee or SLA figure | `IA-15`, `BRU-CAI-02` |

**`IA-16`: content that fails any test is excluded from the corpus, not caveated within it.**
`KB-015` `KR-07` establishes the same asymmetry for knowledge: a human reader can discount a
warning label; a generated answer with a citation cannot convey one credibly.

### 4.9 Coverage and deflection measurement

| Measure | Definition | Target | Source |
|---|---|---|---|
| **Status-enquiry deflection** | Status enquiries resolved in self-service ÷ total status enquiries | **60% W7, 80% W9** | `KPI-025` |
| AI first-contact resolution | | 40% W7, 55% W9 | `KPI-026` |
| First-contact resolution, all channels | **Measured alongside deflection, never instead of it** | 70% W7, 78% W9 | `KPI-027` |
| **Search-to-nothing rate** | Searches returning no result the user opened | Falling; **the coverage gap signal** | `M61` search analytics |
| **Search-then-contact rate** | Sessions where the user searched, then contacted | **Falling — the findability signal** | `M27` + help analytics |
| Article helpfulness | "Did this answer your question?" | > 70% yes | `CG-014` |
| Coverage of top contact reasons | Top 100 contact reasons with a published article | **100%** | `HC-015` + `M27` disposition data |
| Reading completion | Proportion reaching the end of the article | Diagnostic | Help analytics |

**`IA-17`: search-then-contact is the architecture's own report card.** A customer who searched and
then called found nothing usable. It is the only measure that isolates *findability* from *coverage*,
and it is available for free.

### 4.10 Governing rules

| # | Rule | Class |
|---|---|:--:|
| **IA-01** | `P06` help serves existing audiences in a different mode, not a twelfth audience | **C** |
| **IA-02** | Five help object types; the set is closed | **H** |
| **IA-03** | One canonical category tree, projected per audience | **H** |
| **IA-04** | Maximum depth three levels | **H** |
| **IA-05** | No help facet duplicates a `KB` facet under a different name | **H** |
| **IA-06** | A derivative names its source article and version, and is flagged on source change | **C** |
| **IA-07** | A customer article never instructs a consumer to perform a competence-gated hazardous procedure | **H** |
| **IA-08** | Symptom-led navigation is a first-class entry point bound to `MD-024` | **H** |
| **IA-09** | Usable on 3G on a low-end Android | **H** |
| **IA-10** | At most five related links | **S** |
| **IA-11** | Cross-links stay within the audience projection | **H** |
| **IA-12** | Link rather than restate (`CP-01`) | **H** |
| **IA-13** | Every article carries a route to a human | **H** |
| **IA-14** | Help never restates a legal term | **H** |
| **IA-15** | Help never states a price, fee or SLA figure | **H** |
| **IA-16** | Corpus-boundary failures are excluded, not caveated | **C** |
| **IA-17** | Search-then-contact is reported as the findability measure | **C** |
| **IA-18** | Every article declares `help_audience`, `portal`, `journey_stage` and `object_type` before publication | **H** |
| **IA-19** | Bengali is a publication condition for customer- and field-facing audiences, not a follow-up (`CG-010`) | **H** |
| **IA-20** | An article with no measured use in two review cycles is reviewed for retirement (`KB-015` pattern) | **C** |

> Class: **H** hard block · **A** approved override · **S** soft warning · **C** computed — the same
> scale as `05-05` §1.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`../07_Knowledge_Base_and_Technical_Library/KB-001_Knowledge_Architecture_and_Tagging_Standard.md`](../07_Knowledge_Base_and_Technical_Library/KB-001_Knowledge_Architecture_and_Tagging_Standard.md) | The facet spine reused in §4.4; the `O-04` decision this file discharges |
| [`../07_Knowledge_Base_and_Technical_Library/KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md`](../07_Knowledge_Base_and_Technical_Library/KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md) | Source-change flagging in `IA-06`; corpus asymmetry in `IA-16` |
| [`../07_Knowledge_Base_and_Technical_Library/KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](../07_Knowledge_Base_and_Technical_Library/KB-013_ESD_Chemical_and_Battery_Safety_Data.md) | The hazard classification behind `IA-07` |
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md) | `is_customer_selectable` symptoms behind `IA-08` |
| [`HC-002_Help_Article_Template_and_Style_Rules.md`](HC-002_Help_Article_Template_and_Style_Rules.md) | The shape inside the objects this file indexes |
| [`../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) · [`../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) | Reading level and one approved term |
| `M61` FR-KMS-022 · `M32` FR-CAI-015 · `M27` | Delivery, grounding and contact data |
| `RP-001` KPI dictionary | `KPI-025`, `-026`, `-027` definitions |

| Depended on by |
|---|
| `HC-002`…`HC-020` — every file in this category · `M32` corpus configuration · `P01` self-service · `M61` customer publication path |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Annual**, and at every wave boundary that adds a portal |
| Trigger for out-of-cycle review | `KPI-025` missed for two quarters · search-then-contact rising · a new audience · a `KB-001` facet change |
| Owner | Content Design, with Customer Service Manager accountable for the deflection outcome |
| Change log | `RF-006` |
| Enforcement | `IA-01`…`IA-20`; `CG-008` Definition of Done; corpus admission test §4.8 |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`MD-024` is unpopulated** (`AUDIT-008` KB-11), so the customer-selectable symptom set that `IA-08` makes the front door does not exist. **Symptom-led navigation is the single highest-value entry point and it has no content** | Technical analyst (MDM) with Content Design | **W2 — blocking** |
| **O-02** | **`RP-001` KPI dictionary is unwritten** (Category 14 unstarted). §4.9 defines seven measures; three cite `06-02` KPI IDs and the rest need definitions nobody owns | BI Lead with Content Design | **W2** |
| **O-03** | Whether portal search supports **facet-scoped, transliteration-aware bilingual retrieval** across `HC` and `KB` in one index is unconfirmed. §4.4's reuse decision assumes one index; two indexes would reintroduce the drift the decision avoids | CTO with Knowledge Manager | **Before W2 build** |
| **O-04** | **The `KB` → `HC` derivative workflow has no owner.** `IA-06` requires source-change flagging and `BRU-KMS-11` requires dual approval; `M61` provides the mechanism at **W6**, four waves after `HC-003` is due | Knowledge Manager with Customer Service Manager | **W2 — interim manual process needed** |
| **O-05** | `HC-008` `P06` analytics help is registered as a portal help set but §4.1 establishes it is a *mode*, not an audience. The register row's audience description needs a clarifying note (finding **HC-06**) | Programme Content Lead | W4 |
| **O-06** | The eleven audiences include four external populations (`P05`, `P07`, `P08`, `P12`) whose **onboarding content is Category 18 `EO`**, unstarted. The boundary between "help" and "onboarding" for those audiences is undefined | Content Design with Programme Content Lead | W3 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — all six sections present, §7 added per category convention
- [x] **`KB-001` `O-04` decided, with the reasoning recorded so it can be re-examined (§4.4)**
- [x] Audience model enumerated and the eleven-versus-twelve discrepancy explained rather than papered over (`IA-01`)
- [x] Object types closed; two adjacent object classes explicitly placed outside
- [x] One category tree projected per audience, depth-bounded
- [x] `KB` → `HC` derivative boundary stated with the `BRU-KMS-11` dual approval and the no-auto-propagation rule
- [x] Consumer-hazard prohibition stated (`IA-07`)
- [x] Symptom-led navigation made a first-class entry point bound to `MD-024`
- [x] 3G / low-end-Android usability made an architecture constraint
- [x] Deflection paired with first-contact resolution so one is not bought with the other (`IA-13`, §4.9)
- [x] Search-then-contact identified as the findability measure
- [x] `M32` corpus boundary stated as a computable test
- [x] All internal links resolve
- [x] `BRU-KMS-11` cited to `M61` §9; `BRU-CAI-02` cited to `M32` §9; `KPI-025`/`-026`/`-027` to `06-02`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` `MD-024` customer symptoms — outstanding; blocks the primary entry point**
- [ ] **`O-04` derivative workflow owner — outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and Customer Service Manager**
- [x] English-only, per `CG-010` §3.2 — architecture content, head-office audience

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
