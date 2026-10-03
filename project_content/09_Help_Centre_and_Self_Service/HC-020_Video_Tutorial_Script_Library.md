---
id: HC-020
title: Video Tutorial Script Library
project: 1000FiX ERP System v2.0
content_type: Help article
template: TPL_Help_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design
author: Content Design with Customer Experience
reviewers: [Customer Service Manager, Localisation Lead, Accessibility reviewer, Technical Director, HSE Lead, Programme Content Lead]
approver: Content Design Lead
content_class: D
purpose: >
  The scripts for the short how-to videos embedded in help and used by the contact centre. Video is
  the most effective format for low-literacy and first-time users and the most expensive to
  reshoot — a script that is wrong costs a production day, a studio, a presenter and a translation
  cycle, so the scripts must be right before anything is filmed.
traces_to: [M27, M32, M61, P01, P02, P07, P09, HC-001, HC-002, HC-003, HC-004, HC-009, HC-011, HC-015, HC-016, MM-001, MM-007, CG-011, VB-009, TR-003, TR-024]
priority: P3
wave: W6
bilingual: yes
bn_counterpart: HC-020_Video_Tutorial_Script_Library_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P01 Bengali-first for 250,000+ customers a month; P07 sellers with low English literacy; P02 and P09 field workforces with mixed literacy
    verified: 2026-08-18
    class: P1
  - source: project_content/08_Training_and_Enablement/08A_Framework/TR-003_Course_Design_Standard_and_Storyboard_Template.md DS-24, DS-25 — video is for technique that must be seen, not for step-by-step procedure a learner must follow mid-task; production does not begin without an approved storyboard
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md — captions and text alternatives are contractual under WCAG 2.1 AA
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Video Tutorial Script Library

| Item | Value |
|---|---|
| Portal | `P01`, `P02`, `P07`, `P09` primarily; others by exception |
| Audience | **Low-literacy and first-time users** across audiences 1, 2, 6 and 8 |
| Article type | **Script** — supporting the help sets, not a help object type in itself |
| Reading level target | `CG-011`; **scripts are heard, not read** |
| Languages | **Bengali authored and filmed**; English a separate production, not a subtitle |
| Related UI copy | Per the source article's portal pack |

> **Template conformance.** `TPL_Help_Article.md` applied at library level, as `CG-009` §3 requires
> for the 15 help-article files. All sections retained in order with library-level interpretation.
>
> **Note on scope.** This file holds **scripts**. The produced video assets are `MM-007`
> (Category 19, **written 2026-08-18**), and the production specification is `MM-001`. Scripts here; pixels
> there (`CP-01`).

---

## Before you start

| Prerequisite | Why |
|---|---|
| [`HC-001_Help_Centre_Information_Architecture.md`](HC-001_Help_Centre_Information_Architecture.md) · [`HC-002_Help_Article_Template_and_Style_Rules.md`](HC-002_Help_Article_Template_and_Style_Rules.md) | Every video derives from an article (`VS-01`) |
| **The source article, published** | `VS-01` — a video with no article behind it has no reviewed content |
| `MM-001` production specification | Format, resolution, compression — **written; §4.5 encoding ladder and §4.7 accessibility deliverables apply** |
| `TS-002` sandbox | Screen recordings come from sandbox, never production (`HS-19`) |

**`VS-01`: every video derives from a published help article and names it.** The article is the
reviewed content; the script is a rendering of it. This is the same rule `KB-016` `RC-01` applies
to reference cards, and for the same reason — an unreviewed artefact in a trusted position.

---

## Steps — *the script standard and the library*

### The case for video, and its limit

**`VS-02`: video is used where reading is the barrier, not where the task is long.**

| Video is right for | Video is wrong for |
|---|---|
| A first-time task for a low-literacy user | A reference the user needs mid-task |
| Something physical — photographing documents, packing, handling | A decision tree |
| A task whose difficulty is spatial — where to find something | Anything the user must follow step by step while doing it |
| Building confidence before a first attempt | Troubleshooting, where the user needs to jump to their symptom |

`TR-003` `DS-24` states the boundary for training and it holds here: **a user mid-task cannot scrub
a video to find step 7.**

### Script rules

| # | Rule | Class |
|---|---|:--:|
| **VS-01** | Every video derives from a published article and names it | **H** |
| **VS-03** | **Maximum 90 seconds.** Longer is two videos or the wrong format (`AU-25` pattern) | **H** |
| **VS-04** | **The first 5 seconds state what the video will let you do.** Nobody watches a preamble |
| **VS-05** | One task per video. A video covering two tasks is two videos | **H** |
| **VS-06** | Written for **speaking**, not for reading aloud — short sentences, one idea each (`DS-19`) | **H** |
| **VS-07** | **Bengali is authored and filmed, not subtitled.** An English video with Bengali subtitles fails the audience it exists for (`HS-29`) | **H** |
| **VS-08** | **Captions in both languages are mandatory** — `CG-011`, and because much of this audience watches without sound in public | **H** |
| **VS-09** | Screen recordings come from the sandbox; **no customer-identifiable content** (`HS-19`, `AU-26`) | **H** |
| **VS-10** | UI labels spoken and shown match `UI-002`/`UI-003` (`HS-08`) | **H** |
| **VS-11** | **No presenter claims, promises, prices or timings** — the same commitment boundary as `GD-14`…`GD-19` | **H** |
| **VS-12** | Safety content in a video is approved by HSE and is never abbreviated for pace (`RC-02` pattern) | **H** |
| **VS-13** | Every script is storyboarded and approved **before** production (`DS-25`) | **H** |
| **VS-14** | The script states its shot list, so a reshoot is scoped rather than rediscovered | **C** |
| **VS-15** | A video is reviewed at every release affecting its task; **an orphaned video is withdrawn, not left** (`HS-38`, `TR-024` `RL-04`) | **C** |

> **`VS-15` carries the real cost.** An article orphaned by a UI change is edited in minutes. A
> video orphaned by the same change needs a studio, a presenter, a translation and a production
> cycle. That asymmetry is why `VS-02` limits the library to cases where video genuinely earns its
> place, and why the inventory below is deliberately small.

### The library

**`VS-16`: the library is small by design.** Twenty-two scripts, chosen because reading is the
barrier for that audience and that task.

| # | Script | Source article | Audience | Pri |
|---:|---|---|---|:--:|
| 1 | **Book a repair** | `HC-003` #1 | Customer | **P1** |
| 2 | **Track your repair** | `HC-003` #13 | Customer | **P1** |
| 3 | **Approve an estimate** | `HC-003` #21 | Customer | **P1** |
| 4 | **Pay for your repair** | `HC-003` #25 | Customer | **P1** |
| 5 | What to do before you hand over your device | `HC-003` #11 | Customer | P2 |
| 6 | Make a complaint | `HC-003` #35 | Customer | P2 |
| 7 | Create your account | `HC-003` #6 | Customer | P2 |
| 8 | Collect your device | `HC-003` #30 | Customer | P3 |
| 9 | **Photograph your documents for registration** | `HC-009` #2 | Seller | **P1** — the highest-abandonment step in the register (`HC-009` `PS-18`) |
| 10 | How bidding works | `HC-009` Block B | Seller | P2 |
| 11 | How your commission is calculated | `HC-009` #24 | Seller | P2 |
| 12 | Register as a seller | `HC-009` #1 | Seller | P2 |
| 13 | **Scan a device into your custody** | `HC-011` #6 | Rider | **P1** |
| 14 | **Seal and pack** | `HC-011` #7 | Rider | **P1** |
| 15 | Capture proof of delivery | `HC-011` Block C | Rider | P2 |
| 16 | **Take a payment at the door** | `HC-011` #18 | Rider | P2 |
| 17 | **Working with no signal** | `HC-011` Block E | Rider | P2 |
| 18 | **Take the photographs a claim needs** | `HC-004` #20 | Technician | **P1** |
| 19 | Record what you found | `HC-004` #3 | Technician | P2 |
| 20 | **Check what has synced before you leave** | `HC-004` #11 | Technician | P2 |
| 21 | Request a part | `HC-004` #16 | Technician | P3 |
| 22 | **Register as a supplier** | `HC-007` #1 | Vendor | P3 |

**Library total: 22 scripts · 8 at P1 · 11 at P2 · 3 at P3 · 0 at P0.**

**`VS-17`: scripts 9, 13, 14 and 18 are the four that most justify the format.** Photographing
documents, scanning custody, sealing a package and photographing evidence are all **physical,
spatial tasks performed by low-literacy users** — precisely `VS-02`'s case, and precisely where a
written article performs worst.

---

## What happens next

| Outcome | Measure | Target |
|---|---|---|
| Low-literacy users complete tasks unaided | Task completion by audience | Rising for audiences 1, 6, 8 |
| Seller registration completes | **`P07` onboarding completion** | **> 60%** — script 9 is the lever |
| Evidence quality improves | Claim rejections for poor evidence | Falling — script 18 |
| Custody breaks fall | Custody breaks | **Zero** — scripts 13, 14 |
| Contact centre can send a video instead of explaining | Handling time on the covered tasks | Falling |

---

## If it does not work

| Symptom | Cause | What to do |
|---|---|---|
| Videos not watched | Buried, or too long | `VS-03`, `VS-04`; and check placement in `HC-016` |
| Watched but task still failed | The video shows the happy path only | Add the one failure the user actually hits, or return to the article |
| Bengali videos unwatched | Subtitled rather than filmed in Bengali | **`VS-07` breached** — reshoot |
| Videos orphaned after a release | `VS-15` review not run | Withdraw immediately; do not leave a video showing a UI that no longer exists |
| Library growing past 22 | Video used where an article would do | `VS-02`, `VS-16` — each addition needs the case made |

---

## Related

[`09A_Help_Sets_By_Portal/HC-003_Help_Set_P01_Customer_Portal_and_App.md`](09A_Help_Sets_By_Portal/HC-003_Help_Set_P01_Customer_Portal_and_App.md) · [`09A_Help_Sets_By_Portal/HC-004_Help_Set_P02_Technician_App.md`](09A_Help_Sets_By_Portal/HC-004_Help_Set_P02_Technician_App.md) ·
[`09A_Help_Sets_By_Portal/HC-007_Help_Set_P05_Vendor_and_Supplier_Portal.md`](09A_Help_Sets_By_Portal/HC-007_Help_Set_P05_Vendor_and_Supplier_Portal.md) · [`09A_Help_Sets_By_Portal/HC-009_Help_Set_P07_Marketplace_Seller_Portal.md`](09A_Help_Sets_By_Portal/HC-009_Help_Set_P07_Marketplace_Seller_Portal.md) · [`09A_Help_Sets_By_Portal/HC-011_Help_Set_P09_Logistics_and_Rider_App.md`](09A_Help_Sets_By_Portal/HC-011_Help_Set_P09_Logistics_and_Rider_App.md) — the source articles ·
[`HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md`](HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md) — where videos are surfaced ·
[`../08_Training_and_Enablement/08A_Framework/TR-003_Course_Design_Standard_and_Storyboard_Template.md`](../08_Training_and_Enablement/08A_Framework/TR-003_Course_Design_Standard_and_Storyboard_Template.md) `DS-24`, `DS-25` ·
[`../08_Training_and_Enablement/08B_Course_Packs/TR-024_Release_Training_and_Refresher_Standard.md`](../08_Training_and_Enablement/08B_Course_Packs/TR-024_Release_Training_and_Refresher_Standard.md) — `VS-15` ·
`MM-001` production specification · `MM-007` produced video assets.

---

## Feedback

Watch-through rate, completion, and **task completion after watching** — the only measure that
distinguishes a watched video from a useful one. Reported per script, quarterly.

---

## Coverage and Production Plan *(addition — justified: consistent with the category convention; video carries production cost that scripts alone do not reveal)*

| Item | Position |
|---|---|
| Scripts required | **22** · written **0** |
| Script effort | 22 × 2–3 h = **45–65 hours** |
| **Production effort** | **Not a content cost.** 22 videos × 2 languages = **44 productions**, plus captions, plus reshoots on release. This is `MM-007`'s budget and it is not in the content estimate |
| Sequencing | Scripts 9, 13, 14, 18 (`VS-17`), then the 8 P1 |
| Bengali | **Filmed in Bengali**, not subtitled (`VS-07`) — doubling production, not translation |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`MM-001` and `MM-007` are written** — Category 19 completed 2026-08-18. **Nothing can still be filmed, but for a different reason:** `MM-007` `O-01` records that no production capability, budget, crew or presenters exist, and `MM-007` `O-04` that the sandbox and sample documents script 9 needs do not. **The specification gap is closed; the resourcing gap is not** | Content Design Lead with Finance | **W6** |
| **O-02** | **Video production capability, budget and presenters are not identified.** 44 productions in two languages is a programme, and it appears in no plan | Content Design Lead with Finance | **W6 — it is a budget question, not a content one** |
| **O-03** | **Source articles must be published before scripts are written** (`VS-01`). All 22 depend on help sets that are themselves unwritten | Content Design | W6 |
| **O-04** | `TS-002` sandbox for screen recordings does not exist (`HC-002` `O-02`) | Test Lead | W6 |
| **O-05** | **Script 9 is the highest-value item in the library and its source portal `P07` lands at W7**, one wave after this file. The seller-registration video is needed at W7, not W6 | Content Design with Marketplace Operations | W7 |
| **O-06** | `VS-15` release review will require reshoots with a cost nobody has budgeted. **A video library without a reshoot budget decays faster than an article set** | Content Design Lead with Finance | W6 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Help_Article.md` at library level; additions justified
- [x] **Scripts held here, produced assets in `MM-007` (`CP-01`)**
- [x] Every video required to derive from a published article (`VS-01`)
- [x] The case for video bounded, with the wrong-use cases stated (`VS-02`)
- [x] Length, opening, one-task and speaking-style rules set
- [x] **Bengali filmed, not subtitled (`VS-07`); captions mandatory in both languages (`VS-08`)**
- [x] Commitment boundary carried from `HC-019` into presenter speech (`VS-11`)
- [x] Storyboard approval before production (`VS-13`, `DS-25`)
- [x] **Reshoot asymmetry stated as the reason the library is small (`VS-15`, `VS-16`)**
- [x] 22 scripts enumerated with source article, audience and priority
- [x] The four scripts that most justify the format identified (`VS-17`)
- [x] **Production effort separated from content effort and flagged as unbudgeted**
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` `MM-001`/`MM-007` — outstanding; nothing can be filmed**
- [ ] **`O-02` production capability and budget — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approver recorded — **pending Content Design Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
